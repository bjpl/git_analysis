import pandas as pd
import os
import time
import json
import re
from dotenv import load_dotenv
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging

# Configure logging (set level=logging.DEBUG for extra details)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------- Environment Loading ----------
def load_env():
    """
    Load environment variables from the .env file located in the configs folder.
    """
    dotenv_path = Path("C:/Users/brand/Development/add_tags/configs/.env")
    if not dotenv_path.exists():
        raise FileNotFoundError(f".env file not found at {dotenv_path}. Please create it and add your OPENAI_API_KEY.")
    load_dotenv(dotenv_path)
    logging.info("Environment variables loaded successfully.")

# ---------- Data Loading ----------
def load_data(file_path):
    """
    Load data from a CSV file into a pandas DataFrame.
    """
    try:
        logging.info("Inspecting the first few lines of the file:")
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                logging.info(f"Line {i+1}: {line.strip()}")
                if i >= 10:
                    break

        df = pd.read_csv(file_path, delimiter="\t")
        df.dropna(axis=1, how='all', inplace=True)

        # Rename columns to expected names
        column_mapping = {
            "Word (Spanish)": "target_word",
            "Definition (Spanish)": "definition",
            "Collocations (Spanish)": "examples"
        }
        df.rename(columns=column_mapping, inplace=True)
        if "Word (English)" in df.columns:
            df.rename(columns={"Word (English)": "english_word"}, inplace=True)

        required_columns = ["target_word", "definition", "examples"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        logging.info(f"Data loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")
        return df
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return None

# ---------- Batch Tag Generation ----------
def generate_tags_batch(prompts, tokenizer, model, max_retries=3):
    """
    Generate tags for a batch of prompts.
    
    Args:
        prompts (list of str): Each prompt corresponds to a row's content (target word, definition, examples).
        tokenizer: The model tokenizer.
        model: The language model.
        max_retries (int): Number of retries in case of generation errors.
    
    Returns:
        list of list: A list where each element is the list of tags (or empty list) for the corresponding prompt.
    """
    # System prompt with essential instructions.
    system_prompt = (
        "You are an expert tag generator. For each content item below, generate exactly 3-5 tags that describe "
        "the target word based on its definition and examples. Do not include translations. Output ONLY a JSON array "
        "of tags with no additional text.\n\n"
        "Guidelines:\n"
        "  1. Identify the grammatical category (e.g., noun, verb, adjective).\n"
        "  2. Include broader context keywords (e.g., business, technology).\n"
        "  3. Add usage/location context (e.g., market, classroom).\n"
        "  4. Avoid overly specific or literal terms.\n\n"
        "Examples:\n"
        '  Content: "Rentable\tQue genera ganancias.\tProducto rentable, campaña rentable."\n'
        '  Output: ["adjective", "business", "product"]\n\n'
        '  Content: "Negociar\tLlegar a acuerdos.\tNegociar precios, negociar contratos."\n'
        '  Output: ["verb", "agreement", "business"]\n\n'
        "Now, generate tags for the following content items:"
    )
    # Build full prompts for the batch.
    batch_prompts = [f"{system_prompt}\nUser: {prompt}\nAssistant:" for prompt in prompts]
    logging.debug(f"Batch prompts: {batch_prompts}")

    # Set left padding for decoder-only models and tokenize the batch.
    tokenizer.padding_side = "left"
    inputs = tokenizer(batch_prompts, return_tensors="pt", truncation=True, max_length=512, padding=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    logging.debug(f"Batch tokenized input IDs shape: {inputs['input_ids'].shape}")
    logging.debug(f"Batch attention mask shape: {inputs.get('attention_mask').shape if 'attention_mask' in inputs else 'None'}")

    retries = 0
    success = False
    while retries < max_retries:
        try:
            logging.info("Starting batch generation (deterministic greedy decoding)...")
            start_time = time.time()
            generated_ids = model.generate(
                inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                max_new_tokens=50,
                do_sample=False,  # Deterministic decoding
                eos_token_id=tokenizer.eos_token_id
            )
            gen_time = time.time() - start_time
            logging.info(f"Batch generation completed in {gen_time:.2f} seconds.")
            success = True
            break
        except Exception as e:
            logging.exception("Error during batch generation")
            retries += 1
            time.sleep(1)
    if not success:
        return [[] for _ in prompts]

    # Process outputs for each prompt in the batch.
    batch_outputs = []
    for i in range(generated_ids.shape[0]):
        output_text = tokenizer.decode(generated_ids[i], skip_special_tokens=True)
        logging.debug(f"Raw output for prompt {i}: {output_text}")
        match = re.search(r'(\[.*?\])', output_text, re.DOTALL)
        if match:
            tags_json = match.group(1)
            try:
                tags = json.loads(tags_json)
                logging.debug(f"Extracted JSON for prompt {i}: {tags_json}")
            except json.JSONDecodeError as e:
                logging.warning(f"JSON decode error for prompt {i}: {tags_json}. Error: {e}")
                tags = []
        else:
            logging.warning(f"No JSON array found in output for prompt {i}: {output_text}")
            tags = []
        batch_outputs.append(tags)
    return batch_outputs

# ---------- Enrich Data with Generated Tags ----------
def enrich_data_with_tags(df, tokenizer, model, batch_size=20):
    """
    Process the DataFrame in batches, generating tags for each row.
    """
    df['tags'] = None
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        prompts = [f"{row['target_word']}\t{row['definition']}\t{row['examples']}" for _, row in batch.iterrows()]
        logging.info(f"Processing batch rows {i+1} to {min(i+batch_size, len(df))}")
        tags_list = generate_tags_batch(prompts, tokenizer, model)
        for j, tags in enumerate(tags_list):
            df.at[i+j, 'tags'] = tags
        for idx, tags in zip(batch.index, tags_list):
            logging.info(f"Row {idx+1}: Tags Generated - {tags}")
    return df

# ---------- Save Data to CSV ----------
def save_data(df, output_file_path):
    """
    Save the updated DataFrame to a CSV file.
    """
    try:
        df['tags'] = df['tags'].apply(json.dumps)
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        df.to_csv(output_file_path, index=False)
        logging.info(f"Updated data saved successfully to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving data: {e}")

# ---------- Load Model and Tokenizer ----------
def load_model_and_tokenizer(model_name):
    """
    Load the Qwen2.5-14B-Instruct model and tokenizer, using CUDA if available.
    """
    logging.info("Loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.padding_side = "left"  # Ensure left padding for decoder-only models
    device_map = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map=device_map
        )
        # Override sampling defaults to ensure deterministic behavior
        model.config.do_sample = False
        model.config.temperature = 1.0
        model.config.top_k = 0
        model.config.top_p = 1.0
        logging.info(f"Model loaded successfully on {device_map.upper()}.")
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        raise
    return tokenizer, model

# ---------- Main Execution ----------
if __name__ == "__main__":
    try:
        load_env()

        input_file_path = "data/input_data.csv"
        output_file_path = "output/output_data_with_tags.csv"

        df = load_data(input_file_path)
        if df is None:
            logging.error("Data loading failed. Exiting.")
            exit(1)

        model_name = "Qwen/Qwen2.5-14B-Instruct"
        tokenizer, model = load_model_and_tokenizer(model_name)

        # Use a smaller batch size for testing.
        df = enrich_data_with_tags(df, tokenizer, model, batch_size=10)
        save_data(df, output_file_path)

    except Exception as e:
        logging.exception(f"An error occurred in the main process: {e}")
