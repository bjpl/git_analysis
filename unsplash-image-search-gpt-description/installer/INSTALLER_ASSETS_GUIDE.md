# Installer Assets Guide

This document describes the required assets for creating professional-looking installers for the Unsplash Image Search GPT Description application.

## Required Asset Files

### 1. Application Icon (app_icon.ico)
- **File**: `assets/app_icon.ico`
- **Purpose**: Main application icon displayed in installer, shortcuts, and system tray
- **Requirements**:
  - Format: ICO format with multiple sizes
  - Recommended sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
  - Color depth: 32-bit with alpha channel
  - Design: Should represent the application's purpose (image search + AI)
- **Design Guidelines**:
  - Use clear, recognizable imagery (camera, magnifying glass, brain/AI symbol)
  - Ensure good visibility at small sizes (16x16)
  - Use consistent color scheme with application branding
  - Avoid complex details that don't scale well

### 2. Wizard Left Banner (wizard_left.bmp)
- **File**: `assets/wizard_left.bmp`
- **Purpose**: Large banner image displayed on the left side of installer wizard pages
- **Requirements**:
  - Dimensions: 164 x 314 pixels
  - Format: 24-bit BMP
  - Colors: Should complement application branding
- **Design Guidelines**:
  - Vertical layout optimized for the wizard sidebar
  - Include application logo or relevant imagery
  - Use subtle gradient or professional background
  - Ensure text readability if any text is included
  - Consider the installer's color scheme (typically white/gray)

### 3. Wizard Header Icon (wizard_small.bmp)
- **File**: `assets/wizard_small.bmp`
- **Purpose**: Small icon displayed in the header area of installer wizard pages
- **Requirements**:
  - Dimensions: 55 x 58 pixels
  - Format: 24-bit BMP
  - Should be recognizable even at small size
- **Design Guidelines**:
  - Simplified version of the main application icon
  - Clear, bold design that scales well
  - Consistent with main branding
  - Avoid fine details

### 4. Uninstaller Banner (uninstall_banner.bmp)
- **File**: `assets/uninstall_banner.bmp`
- **Purpose**: Banner image displayed during uninstallation process
- **Requirements**:
  - Dimensions: 164 x 314 pixels (same as wizard banner)
  - Format: 24-bit BMP
- **Design Guidelines**:
  - Can be the same as wizard_left.bmp or a variant
  - Consider using slightly different styling to indicate uninstall process
  - Maintain brand consistency

## Optional Asset Files

### 5. License Files (Multi-language)
- **Files**: 
  - `assets/LICENSE_es.txt` (Spanish)
  - `assets/LICENSE_fr.txt` (French)
  - `assets/LICENSE_de.txt` (German)
- **Purpose**: Localized license agreements
- **Requirements**: Plain text format, properly translated

### 6. Documentation PDFs
- **Files**: `assets/*.pdf`
- **Purpose**: Quick start guides, user manuals
- **Examples**:
  - `quick_start_guide.pdf`
  - `api_setup_guide.pdf`
  - `troubleshooting_guide.pdf`

### 7. Sample Files
- **Directory**: `assets/samples/`
- **Purpose**: Example sessions, configurations, vocabulary lists
- **Examples**:
  - `sample_session.uigd`
  - `example_vocabulary.csv`
  - `demo_configuration.json`

## Creating Assets

### Tools Recommended
- **Icons**: 
  - IcoFX (Free icon editor)
  - GIMP with ICO plugin
  - IconWorkshop
- **Bitmaps**:
  - Adobe Photoshop
  - GIMP
  - Paint.NET
  - Canva (for quick professional designs)

### Color Scheme Recommendations
Based on the application's purpose (image search + AI), consider:
- **Primary Colors**: Blue (#007ACC), Green (#28A745), Purple (#6F42C1)
- **Accent Colors**: Orange (#FD7E14), Teal (#20C997)
- **Neutral Colors**: Gray (#6C757D), White (#FFFFFF)

### Design Resources
- **Icon Libraries**: 
  - Font Awesome
  - Material Design Icons
  - Feather Icons
- **Stock Images**:
  - Unsplash (fitting for the application)
  - Pexels
  - Pixabay

## Asset Creation Checklist

### Before Building Installer
- [ ] All required asset files are present in `assets/` directory
- [ ] Icons include multiple sizes and have alpha channel
- [ ] Bitmaps are correct dimensions and format
- [ ] Colors are consistent with application branding
- [ ] Images are optimized for file size
- [ ] Text in images is readable at target sizes

### Quality Assurance
- [ ] Test installer appearance on different Windows versions
- [ ] Verify icons display correctly in Windows Explorer
- [ ] Check that banner images don't appear distorted
- [ ] Ensure uninstaller branding is consistent
- [ ] Validate that all images load without errors

## Fallback Behavior

If asset files are missing:
- The installer will use default Inno Setup images
- Functionality will not be affected
- Professional appearance may be compromised
- Warning messages will be displayed during build

## File Size Considerations

- **Total asset size should be under 2MB**
- ICO files: typically 100-500KB
- BMP files: approximately 150KB each
- Compress images appropriately without losing quality
- Consider the final installer size impact

## Branding Guidelines

### Professional Appearance
- Maintain consistency across all installer screens
- Use high-quality, professionally designed assets
- Ensure assets reflect the application's purpose and quality
- Consider user experience throughout installation process

### Brand Identity
- Incorporate company/project logo if available
- Use consistent typography (though limited in bitmaps)
- Maintain color harmony
- Create memorable visual identity

## Localization

For international deployment:
- Create localized versions of text-containing images
- Consider cultural color preferences
- Ensure images work with different text directions
- Test with various language installations

## Accessibility

- Use high contrast ratios
- Avoid relying solely on color to convey information
- Ensure images are clear for users with visual impairments
- Consider alternative text descriptions in documentation

## Maintenance

- Update assets when rebranding
- Version control asset files
- Document any design decisions
- Keep source files (PSD, XCF, etc.) for future edits
- Review and update assets with major version releases

---

**Note**: If you need assistance creating these assets, consider hiring a graphic designer or using online design tools like Canva, which offers professional templates for software branding.