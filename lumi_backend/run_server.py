"""
CLI Runner for LUMI Caregiver Backend Server.
"""

from __future__ import annotations

import argparse
import os
import sys
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="LUMI Caregiver Backend Server")
    parser.add_argument("--host", default="0.0.0.0", help="Binding host (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Binding port (default 8000)")
    parser.add_argument("--mock", action="store_true", default=True, help="Force mock development mode")
    parser.add_argument("--ros", action="store_true", help="Enable production ROS 2 mode")
    args = parser.parse_args()

    if args.ros:
        os.environ["LUMI_DEV_MODE"] = "false"
    else:
        os.environ["LUMI_DEV_MODE"] = "true"

    os.environ["LUMI_HOST"] = args.host
    os.environ["LUMI_PORT"] = str(args.port)

    print("=" * 60)
    print(f" Starting LUMI Caregiver Backend on http://{args.host}:{args.port}")
    print(f" Operating Mode: {'MOCK DEV MODE' if os.environ['LUMI_DEV_MODE'] == 'true' else 'PRODUCTION ROS 2'}")
    print(f" REST API: http://{args.host}:{args.port}/api/v1")
    print(f" WebSockets: ws://{args.host}:{args.port}/api/v1/ws")
    print(f" Interactive Docs: http://{args.host}:{args.port}/docs")
    print("=" * 60)

    uvicorn.run("lumi_backend.main:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
