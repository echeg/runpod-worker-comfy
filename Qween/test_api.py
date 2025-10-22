"""
Test script for Qwen-Soloband RunPod Serverless API
"""

import requests
import json
import base64
import os
from pathlib import Path

# Configuration
RUNPOD_ENDPOINT_ID = os.environ.get("RUNPOD_ENDPOINT_ID", "h18zddwdmnyehs")
RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY", "rpa_xxx")

BASE_URL = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}"

HEADERS = {
    "Authorization": f"Bearer {RUNPOD_API_KEY}",
    "Content-Type": "application/json"
}


def test_text2img():
    """Test Text-to-Image generation"""
    print("\n" + "=" * 80)
    print("Testing Text-to-Image")
    print("=" * 80)
    
    payload = {
        "input": {
            "mode": "text2img",
            "prompt": "SB_AI, a beautiful fantasy landscape with mountains, lake, and aurora borealis, highly detailed, 8k uhd",
            "negative_prompt": "blurry, low quality, deformed",
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 40,
            "guidance_scale": 2.5,
            "seed": 42,
            "lora_name": "None",
            "lora_scale": 1.0,
            "scheduler": "flow_euler_shift05"
        }
    }
    
    print("Sending request...")
    response = requests.post(f"{BASE_URL}/runsync", json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        
        if "output" in result:
            print("✅ Generation successful!")
            print(f"   Seed: {result['output']['seed']}")

            # Save image
            image_b64 = result["output"]["image"]
            image_data = base64.b64decode(image_b64)
            
            output_path = Path("test_output_text2img.png")
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            print(f"   Image saved to: {output_path}")
        else:
            print("❌ Error:", result.get("error", "Unknown error"))
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)


def test_img2img():
    """Test Image-to-Image generation"""
    print("\n" + "=" * 80)
    print("Testing Image-to-Image")
    print("=" * 80)
    
    # Check if we have a test image
    test_image_path = Path("test_output_text2img.png")
    if not test_image_path.exists():
        print("⚠️  No test image found. Running text2img first...")
        test_text2img()
    
    # Load and encode image
    with open(test_image_path, "rb") as f:
        input_image_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    payload = {
        "input": {
            "mode": "img2img",
            "input_image": input_image_b64,
            "prompt": "SB_AI, cyberpunk neon city at night, futuristic",
            "negative_prompt": "blurry, low quality",
            "strength": 0.75,
            "num_inference_steps": 40,
            "guidance_scale": 2.5,
            "seed": 123,
            "lora_name": "None",
            "lora_scale": 1.0,
            "scheduler": "flow_euler_shift05"
        }
    }
    
    print("Sending request...")
    response = requests.post(f"{BASE_URL}/runsync", json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        
        if "output" in result:
            print("✅ Generation successful!")
            print(f"   Seed: {result['output']['seed']}")

            # Save image
            image_b64 = result["output"]["image"]
            image_data = base64.b64decode(image_b64)
            
            output_path = Path("test_output_img2img.png")
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            print(f"   Image saved to: {output_path}")
        else:
            print("❌ Error:", result.get("error", "Unknown error"))
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)


def test_list_loras():
    """Test listing available LoRAs"""
    print("\n" + "=" * 80)
    print("Testing List LoRAs")
    print("=" * 80)
    
    payload = {
        "input": {
            "mode": "list_loras"
        }
    }
    
    print("Sending request...")
    response = requests.post(f"{BASE_URL}/runsync", json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        
        if "output" in result:
            print("✅ Request successful!")
            print(f"   Total LoRAs: {result['output']['count']}")
            print(f"   Hub LoRAs: {result['output']['hub_loras']}")
            print(f"   Local LoRAs: {result['output']['local_loras']}")
            print(f"   Available: {result['output']['available_loras']}")
        else:
            print("❌ Error:", result.get("error", "Unknown error"))
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)


def test_with_lora():
    """Test generation with LoRA"""
    print("\n" + "=" * 80)
    print("Testing Text-to-Image with LoRA (Realism)")
    print("=" * 80)
    
    payload = {
        "input": {
            "mode": "text2img",
            "prompt": "portrait of a woman, professional photography",
            "negative_prompt": "blurry, low quality, cartoon, anime",
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 40,
            "guidance_scale": 2.5,
            "seed": 999,
            "lora_name": "Realism",
            "lora_scale": 1.0,
            "scheduler": "flow_euler_shift05"
        }
    }
    
    print("Sending request...")
    response = requests.post(f"{BASE_URL}/runsync", json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        
        if "output" in result:
            print("✅ Generation successful!")
            print(f"   Seed: {result['output']['seed']}")
            print(f"   Generation time: {result['output']['generation_time']:.2f}s")
            
            # Save image
            image_b64 = result["output"]["image"].split(",")[1]
            image_data = base64.b64decode(image_b64)
            
            output_path = Path("test_output_lora_realism.png")
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            print(f"   Image saved to: {output_path}")
        else:
            print("❌ Error:", result.get("error", "Unknown error"))
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("=" * 80)
    print("Qwen-Soloband RunPod Serverless API Test")
    print("=" * 80)
    print(f"Endpoint: {BASE_URL}")
    
    if RUNPOD_ENDPOINT_ID == "your-endpoint-id-here":
        print("\n⚠️  WARNING: Please set RUNPOD_ENDPOINT_ID environment variable!")
        print("   export RUNPOD_ENDPOINT_ID=your-endpoint-id")
        print("   export RUNPOD_API_KEY=your-api-key")
        exit(1)
    
    # Run tests
    test_text2img()
    test_img2img()
    test_with_lora()
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)

