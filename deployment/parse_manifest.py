import yaml
import sys
import os

def generate_requirements(manifest_path='service-manifest.yaml', output_path='manifest_requirements.txt'):
    """
    Parses the service manifest and generates a pip requirements file.
    """
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest file '{manifest_path}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        try:
            manifest = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing manifest: {e}", file=sys.stderr)
            sys.exit(1)
    
    services = manifest.get('services', {})
    
    with open(output_path, 'w') as out:
        for service, config in services.items():
            version = config.get('version', '').lstrip('v')
            if version:
                out.write(f"{service}=={version}\n")
            else:
                out.write(f"{service}\n")
                
    print(f"Successfully generated {output_path} with {len(services)} services.")

if __name__ == "__main__":
    generate_requirements()
