"""
Hathor Network Client

Handles wallet operations and blockchain interactions for the Hathor network.
"""

import hashlib
import logging
import os
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Hathor configuration
HATHOR_NETWORK = os.getenv("HATHOR_NETWORK", "testnet")
HATHOR_NODE_URL = os.getenv("HATHOR_NODE_URL", "https://node1.testnet.hathor.network")
HATHOR_WALLET_SEED = os.getenv("HATHOR_WALLET_SEED")

# In-memory storage for user addresses
user_addresses: Dict[str, str] = {}  # user_id -> address


class HathorClient:
    """Client for interacting with Hathor network."""
    
    def __init__(self, node_url: str = HATHOR_NODE_URL):
        self.node_url = node_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'WhatsPayAI/1.0'
        })
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: dict = None) -> Optional[dict]:
        """Make HTTP request to Hathor node."""
        try:
            url = f"{self.node_url}/{endpoint.lstrip('/')}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=data)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Hathor API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Hathor request: {e}")
            return None
    
    def get_address_info(self, address: str) -> Optional[dict]:
        """Get address information including balance and transactions."""
        return self._make_request(f"thin_wallet/address_info", 'GET', {'address': address})
    
    def get_address_history(self, address: str) -> Optional[dict]:
        """Get transaction history for an address."""
        return self._make_request(f"thin_wallet/address_history", 'GET', {'address': address})


# Global Hathor client instance
hathor_client = HathorClient()


def generate_deterministic_address(user_id: str) -> str:
    """
    Generate a deterministic Hathor address for a user.
    
    Note: This is a simplified implementation. In production, you should use
    proper HD wallet derivation with the hathor-wallet-lib.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        Hathor address string
    """
    if user_id in user_addresses:
        return user_addresses[user_id]
    
    try:
        # Create deterministic seed from user_id and wallet seed
        if not HATHOR_WALLET_SEED:
            raise ValueError("HATHOR_WALLET_SEED not configured")
        
        # Simple deterministic address generation (simplified for demo)
        combined_seed = f"{HATHOR_WALLET_SEED}:{user_id}"
        address_hash = hashlib.sha256(combined_seed.encode()).hexdigest()
        
        # Generate mock Hathor address format (in production, use proper derivation)
        if HATHOR_NETWORK == "testnet":
            address = f"WYBwT{address_hash[:30]}"  # Testnet prefix
        else:
            address = f"H{address_hash[:33]}"  # Mainnet prefix
        
        user_addresses[user_id] = address
        logger.info(f"Generated address {address} for user {user_id}")
        
        return address
        
    except Exception as e:
        logger.error(f"Failed to generate address for user {user_id}: {e}")
        # Return a mock address for development
        return "WYBwT1234567890abcdef1234567890"


def get_user_address(user_id: str) -> str:
    """
    Get or generate a Hathor address for a user.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        Hathor address string
    """
    if user_id in user_addresses:
        return user_addresses[user_id]
    
    return generate_deterministic_address(user_id)


def check_incoming_deposits(address: str) -> List[Tuple[str, float]]:
    """
    Check for new incoming deposits to an address.
    
    Args:
        address: Hathor address to check
        
    Returns:
        List of (transaction_hash, amount) tuples
    """
    try:
        # Get address history
        history = hathor_client.get_address_history(address)
        if not history or not history.get('success'):
            logger.warning(f"Failed to get history for address {address}")
            return []
        
        deposits = []
        transactions = history.get('history', [])
        
        for tx in transactions:
            # Check if this is an incoming transaction
            for output in tx.get('outputs', []):
                if output.get('decoded', {}).get('address') == address:
                    amount = output.get('value', 0) / 100  # Convert from centis to HTR
                    if amount > 0:
                        deposits.append((tx.get('tx_id'), amount))
        
        return deposits
        
    except Exception as e:
        logger.error(f"Error checking deposits for address {address}: {e}")
        return []


def get_address_balance(address: str) -> float:
    """
    Get the current balance of a Hathor address.
    
    Args:
        address: Hathor address to check
        
    Returns:
        Balance in HTR tokens
    """
    try:
        info = hathor_client.get_address_info(address)
        if not info or not info.get('success'):
            logger.warning(f"Failed to get info for address {address}")
            return 0.0
        
        # Convert from centis to HTR
        balance = info.get('total_amount_received', 0) / 100
        return balance
        
    except Exception as e:
        logger.error(f"Error getting balance for address {address}: {e}")
        return 0.0


def submit_transfer(from_address: str, to_address: str, amount: float) -> Optional[str]:
    """
    Submit a transfer transaction (placeholder implementation).
    
    Note: This is a simplified placeholder. In production, you would need to:
    1. Use proper wallet management with private keys
    2. Build and sign transactions using hathor-wallet-lib
    3. Submit to the network
    
    Args:
        from_address: Sender address
        to_address: Recipient address
        amount: Amount in HTR tokens
        
    Returns:
        Transaction hash if successful, None otherwise
    """
    logger.warning("Transfer functionality not implemented - this is a placeholder")
    
    # In a real implementation, you would:
    # 1. Load the private key for from_address
    # 2. Create a transaction using hathor-wallet-lib
    # 3. Sign the transaction
    # 4. Submit to the network
    
    return None


def validate_hathor_address(address: str) -> bool:
    """
    Validate a Hathor address format.
    
    Args:
        address: Address string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not address or not isinstance(address, str):
        return False
    
    # Basic validation for Hathor address format
    if HATHOR_NETWORK == "testnet":
        return address.startswith("WYBwT") and len(address) >= 30
    else:
        return address.startswith("H") and len(address) >= 30
