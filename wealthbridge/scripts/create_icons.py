
# scripts/create_icons.py
from PIL import Image
import os
import json
import sys

def create_pwa_icons():
    """Create all PWA icons for SkyBridge Bank."""
    
    # Get project paths - icons go in /static/images/
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_images = os.path.join(project_root, 'static', 'images', 'blue.png')  # Your original
    output_dir = os.path.join(project_root, 'static', 'images')
    
    print(f"[DIR] Project root: {project_root}")
    print(f"[IMG] Source images: {source_images}")
    
    # Check source exists
    if not os.path.exists(source_images):
        print(f"[ERROR] Source images not found at {source_images}")
        print("Please add your blue.png to static/images/")
        return False
    
    # Sizes from your manifest.json
    manifest_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    # Additional needed sizes
    extra_sizes = [16, 32, 48, 180]  # For favicon, apple touch icon, etc.
    
    all_sizes = sorted(set(manifest_sizes + extra_sizes))
    
    try:
        with Image.open(source_images) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            print("\nCreating PWA icons...")
            
            # 1. Create all icon sizes
            for size in all_sizes:
                output_path = os.path.join(output_dir, f'blue-{size}x{size}.png')
                img.resize((size, size), Image.LANCZOS).save(output_path, 'PNG')
                print(f"  - Created: blue-{size}x{size}.png")
            
            # 2. Create favicon.ico (combines 16x16, 32x32, 48x48)
            favicon_path = os.path.join(output_dir, 'favicon.ico')
            favicon_sizes = [16, 32, 48]
            favicon_images = [img.resize((s, s), Image.LANCZOS) for s in favicon_sizes]
            favicon_images[0].save(favicon_path, format='ICO', sizes=[(s, s) for s in favicon_sizes])
            print(f"  - Created: favicon.ico")
            
            # 3. Create screenshot images (if needed)
            screenshot_path = os.path.join(output_dir, 'blue-screenshot.png')
            try:
                # Create a screenshot placeholder (you should replace with actual screenshot)
                screenshot = img.resize((1170, 2532), Image.LANCZOS)
                screenshot.save(screenshot_path, 'PNG')
                print(f"  - Created placeholder: blue-screenshot.png")
                print(f"    [WARNING] Replace with actual 1170x2532 screenshot")
            except:
                print(f"  [WARNING] Could not create screenshot placeholder")
            
            print("\nIcons created successfully!")
            print(f"\nFiles saved to: {output_dir}/")
            
            return True
            
    except ImportError:
        print("\n❌ Pillow not installed.")
        print("Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_pwa_icons()
    sys.exit(0 if success else 1)
