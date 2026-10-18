#!/usr/bin/env python3
"""
Single-frame / Stream Inference Script for Thermal YOLOv8n Uniform Detection
Demonstrates how to download from Hugging Face Hub (or load locally) and run inference.
"""

import os
import argparse
import numpy as np

def run_inference(model_path, image_path=None):
    print(f"Loading YOLOv8n detection model from: {model_path}")
    
    if model_path.endswith(".onnx"):
        import onnxruntime as ort
        session = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        input_name = session.get_inputs()[0].name
        
        # Simulated or loaded thermal 640x640 letterbox image [1, 3, 640, 640] normalized to [0, 1]
        dummy_input = np.random.uniform(0.0, 1.0, (1, 3, 640, 640)).astype(np.float32)
        outputs = session.run(None, {input_name: dummy_input})
        output_tensor = outputs[0]
        print(f"Inference successful!")
        print(f"Output shape: {output_tensor.shape}") # [1, 5, 8400] -> (cx, cy, w, h, uniform_conf)
        print(f"Class: uniform (0)")
        return output_tensor
        
    elif model_path.endswith(".pt"):
        from ultralytics import YOLO
        model = YOLO(model_path)
        print(f"Loaded PyTorch checkpoint. Class names: {model.names}")
        # Run mock forward
        dummy_frame = (np.random.uniform(0, 255, (640, 640, 3))).astype(np.uint8)
        results = model.predict(dummy_frame, verbose=False)
        print(f"Inference completed. Results: {len(results)} image(s) processed.")
        return results

    elif model_path.endswith(".engine"):
        print("TensorRT engine specified. Run with trtexec or Jetson TensorRT python runtime.")
        print(f"Engine path: {model_path}")
        return None
    else:
        raise ValueError(f"Unsupported format: {model_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="models/best.onnx", help="Path to ONNX, PT or Engine")
    args = parser.parse_args()
    run_inference(args.model)
