<script>
  import Homepage from './pages/Homepage.svelte';
</script>

<Homepage />

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  :global(*, *::before, *::after) {
    box-sizing: inherit;
  }
  
  :global(.prose) {
    max-width: none;
  }
</style>