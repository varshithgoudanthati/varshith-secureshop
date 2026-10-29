import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from secureshop import create_app
from secureshop.config import SecureConfig, VulnerableConfig
from secureshop.seed import seed_database

def parse_arguments():
    parser = argparse.ArgumentParser(description="SecureShop — Red Team Application Security Lab")
    parser.add_argument(
        "--mode",
        choices=["secure", "vulnerable"],
        default=os.environ.get("SECURESHOP_MODE", "secure").lower(),
        help="Execution profile: 'secure' (default, hardened) or 'vulnerable' (lab educational testing)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 5000)),
        help="Port to listen on (default: 5000)"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Force re-seed sample users, products, and orders"
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    os.environ["SECURESHOP_MODE"] = args.mode

    db_path = os.environ.get("DATABASE_PATH", "instance/secureshop.db")
    if not os.path.exists(db_path) or args.seed:
        print(f"[*] Initializing and seeding database at {db_path}...")
        seed_database(db_path)

    if args.mode == "vulnerable":
        config = VulnerableConfig()
        print("\n" + "=" * 70)
        print("⚠️  WARNING: STARTING SECURESHOP IN VULNERABLE LAB MODE")
        print("    OWASP Top 10 weaknesses (A01, A03, A05, A07, A09) are active.")
        print("    Strictly bound to 127.0.0.1 for local educational analysis only.")
        print("=" * 70 + "\n")
        app = create_app(config)
        # Never bind to 0.0.0.0 in vulnerable mode for safety
        app.run(host="127.0.0.1", port=args.port, debug=True)
    else:
        config = SecureConfig()
        print("\n" + "=" * 70)
        print("🛡️  STARTING SECURESHOP IN SECURE HARDENED MODE (DEFAULT)")
        print("    Defenses Active: Parameterized SQL, CSRF tokens, Session Hardening,")
        print("    Object Authorization, Security Headers, and Sanitized Error Handling.")
        print("=" * 70 + "\n")
        app = create_app(config)
        app.run(host="127.0.0.1", port=args.port, debug=False)

if __name__ == "__main__":
    main()
