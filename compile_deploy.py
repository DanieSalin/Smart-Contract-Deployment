#!/usr/bin/env python3
"""
Script biên dịch và triển khai Smart Contract trên mạng Ethereum Sepolia.
Phần 1: Biên dịch smart contract Solidity
Phần 2: Triển khai smart contract đã biên dịch
Phần 3: Tương tác với smart contract đã triển khai
"""

import os
import json
import solcx
from web3 import Web3
from eth_account import Account
import time

# Cấu hình kết nối đến mạng Sepolia thông qua Infura
INFURA_URL = "https://sepolia.infura.io/v3/{URL_INFURA_YOUR_API_KEY}"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Thêm middleware cho mạng PoA (Proof of Authority)
try:
    from web3.middleware.geth import geth_poa_middleware
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print("Đã thêm middleware cho mạng PoA")
except ImportError:
    print("Cảnh báo: Không thể import geth_poa_middleware")

# Kiểm tra kết nối
print(f"Kết nối đến Ethereum Sepolia: {w3.is_connected()}")
print(f"Chain ID: {w3.eth.chain_id}")

# Đường dẫn đến file contract
CONTRACT_PATH = os.path.join("src", "SimpleToken.sol")
COMPILED_PATH = os.path.join("build", "SimpleToken.json")


def create_account():
    """Tạo một tài khoản Ethereum mới"""
    account = Account.create()
    private_key = account.key.hex()
    address = account.address
    
    print(f"\n=== Tài khoản mới ===")
    print(f"Địa chỉ: {address}")
    print(f"Private key: {private_key}")
    print("LƯU Ý: KHÔNG BAO GIỜ chia sẻ private key của bạn!")
    
    return private_key, address


def save_account_info(private_key, address, filename="account_info.json"):
    """Lưu thông tin tài khoản vào file JSON"""
    account_info = {
        "address": address,
        "private_key": private_key
    }
    
    # Tạo thư mục build nếu chưa tồn tại
    os.makedirs("build", exist_ok=True)
    
    path = os.path.join("build", filename)
    with open(path, "w") as f:
        json.dump(account_info, f)
    
    print(f"\nĐã lưu thông tin tài khoản vào {path}")


def load_account_info(filename="account_info.json"):
    """Đọc thông tin tài khoản từ file JSON"""
    path = os.path.join("build", filename)
    try:
        with open(path, "r") as f:
            account_info = json.load(f)
        return account_info.get("private_key"), account_info.get("address")
    except FileNotFoundError:
        print(f"Không tìm thấy file {path}")
        return None, None


def compile_contract():
    """Biên dịch smart contract Solidity"""
    print("\n=== Biên dịch Smart Contract ===")
    
    # Cài đặt phiên bản solc
    solc_version = "0.8.19"
    try:
        solcx.install_solc(solc_version)
        solcx.set_solc_version(solc_version)
        print(f"Đã cài đặt trình biên dịch Solidity phiên bản {solc_version}")
    except Exception as e:
        print(f"Lỗi khi cài đặt trình biên dịch Solidity: {e}")
        return None
    
    try:
        # Kiểm tra xem tệp contract có tồn tại không
        if not os.path.exists(CONTRACT_PATH):
            print(f"Lỗi: Không tìm thấy tệp contract tại {CONTRACT_PATH}")
            return None
            
        print(f"Đường dẫn đến contract: {os.path.abspath(CONTRACT_PATH)}")
        
        # Biên dịch contract
        compiled_sol = solcx.compile_files(
            [CONTRACT_PATH],
            output_values=["abi", "bin"],
            optimize=True,
            optimize_runs=200
        )
        
        # In ra các khóa trong kết quả biên dịch để debug
        print(f"Các contract đã biên dịch: {list(compiled_sol.keys())}")
        
        # Lấy thông tin contract (sử dụng cách đúng tùy theo phiên bản solc)
        contract_id = ""
        for key in compiled_sol.keys():
            if key.endswith(":SimpleToken"):
                contract_id = key
                break
        
        if not contract_id:
            print("Không tìm thấy contract SimpleToken trong kết quả biên dịch")
            return None
        
        print(f"Contract ID: {contract_id}")
        contract_interface = compiled_sol[contract_id]
        
        # Tạo thư mục build nếu chưa tồn tại
        os.makedirs("build", exist_ok=True)
        
        # Lưu thông tin biên dịch vào file JSON
        with open(COMPILED_PATH, "w") as f:
            json.dump(contract_interface, f)
        
        print(f"Đã biên dịch thành công và lưu vào {COMPILED_PATH}")
        return contract_interface
    except Exception as e:
        print(f"Lỗi khi biên dịch contract: {e}")
        print(f"Danh sách các contract_id trong compiled_sol: {list(compiled_sol.keys()) if 'compiled_sol' in locals() else 'Không có'}")
        return None


def deploy_contract(private_key, contract_interface, constructor_args):
    """Triển khai smart contract đã biên dịch"""
    print("\n=== Triển khai Smart Contract ===")
    
    # Lấy thông tin tài khoản
    account = Account.from_key(private_key)
    address = account.address
    
    # Lấy ABI và bytecode
    abi = contract_interface["abi"]
    bytecode = contract_interface["bin"]
    
    # Tạo instance của contract
    SimpleToken = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    try:
        # Lấy nonce
        nonce = w3.eth.get_transaction_count(address)
        
        # Xây dựng giao dịch triển khai
        transaction = SimpleToken.constructor(*constructor_args).build_transaction({
            "from": address,
            "nonce": nonce,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price,
            "chainId": w3.eth.chain_id
        })
        
        # Ký giao dịch
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key)
        
        # Gửi giao dịch
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Giao dịch triển khai đã được gửi: {tx_hash.hex()}")
        
        # Đợi giao dịch được xác nhận
        print("Đang đợi giao dịch được xác nhận...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        contract_address = tx_receipt.contractAddress
        print(f"Contract đã được triển khai tại địa chỉ: {contract_address}")
        
        # Lưu địa chỉ contract vào file
        with open(os.path.join("build", "contract_address.txt"), "w") as f:
            f.write(contract_address)
        
        return contract_address, abi
    except Exception as e:
        print(f"Lỗi khi triển khai contract: {e}")
        return None, None


def verify_deployment(contract_address, abi):
    """Xác minh contract đã được triển khai thành công"""
    print("\n=== Xác minh triển khai Smart Contract ===")
    
    try:
        # Tạo instance của contract đã triển khai
        token_contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Gọi các hàm để lấy thông tin token
        name = token_contract.functions.name().call()
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()
        total_supply = token_contract.functions.totalSupply().call()
        
        print(f"Thông tin Token:")
        print(f"- Tên: {name}")
        print(f"- Ký hiệu: {symbol}")
        print(f"- Số thập phân: {decimals}")
        print(f"- Tổng cung: {total_supply / (10 ** decimals)} {symbol}")
        
        return True
    except Exception as e:
        print(f"Lỗi khi xác minh contract: {e}")
        return False


def interact_with_contract(contract_address, abi, private_key, to_address, amount):
    """Tương tác với smart contract đã triển khai"""
    print("\n=== Tương tác với Smart Contract ===")
    
    # Lấy thông tin tài khoản
    account = Account.from_key(private_key)
    from_address = account.address
    
    try:
        # Tạo instance của contract đã triển khai
        token_contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Kiểm tra số dư của người gửi
        decimals = token_contract.functions.decimals().call()
        balance = token_contract.functions.balanceOf(from_address).call()
        symbol = token_contract.functions.symbol().call()
        
        print(f"Số dư của {from_address}: {balance / (10 ** decimals)} {symbol}")
        
        # Chuyển đổi số lượng token từ đơn vị token sang wei
        amount_wei = int(amount * (10 ** decimals))
        
        if balance < amount_wei:
            print(f"Không đủ token. Số dư: {balance / (10 ** decimals)} {symbol}, Cần chuyển: {amount} {symbol}")
            return False
        
        # Lấy nonce
        nonce = w3.eth.get_transaction_count(from_address)
        
        # Xây dựng giao dịch transfer
        transaction = token_contract.functions.transfer(
            to_address, 
            amount_wei
        ).build_transaction({
            "from": from_address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
            "chainId": w3.eth.chain_id
        })
        
        # Ký giao dịch
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key)
        
        # Gửi giao dịch
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Giao dịch transfer đã được gửi: {tx_hash.hex()}")
        
        # Đợi giao dịch được xác nhận
        print("Đang đợi giao dịch được xác nhận...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            print(f"Giao dịch thành công!")
            
            # Kiểm tra số dư sau khi chuyển
            new_balance_from = token_contract.functions.balanceOf(from_address).call()
            new_balance_to = token_contract.functions.balanceOf(to_address).call()
            
            print(f"Số dư mới của người gửi {from_address}: {new_balance_from / (10 ** decimals)} {symbol}")
            print(f"Số dư mới của người nhận {to_address}: {new_balance_to / (10 ** decimals)} {symbol}")
            
            return True
        else:
            print(f"Giao dịch thất bại!")
            return False
    except Exception as e:
        print(f"Lỗi khi tương tác với contract: {e}")
        return False


def main():
    print("=== TRIỂN KHAI VÀ TƯƠNG TÁC VỚI TOKEN ERC-20 ===")
    
    # Tạo hoặc tải thông tin tài khoản
    private_key, address = load_account_info()
    
    if not private_key or not address:
        print("Không tìm thấy thông tin tài khoản hiện có. Tạo tài khoản mới...")
        private_key, address = create_account()
        save_account_info(private_key, address)
    else:
        print(f"\n=== Thông tin tài khoản ===")
        print(f"Địa chỉ: {address}")
        print(f"Private key: {private_key[:6]}...{private_key[-4:]}")
    
    # Kiểm tra số dư ETH
    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance_wei, "ether")
    print(f"\nSố dư: {balance_eth} ETH")
    
    if balance_wei == 0:
        print("\nCẢNH BÁO: Tài khoản không có ETH. Bạn sẽ không thể triển khai smart contract.")
        print("Bạn cần nhận ETH testnet từ một trong các faucet sau:")
        print("1. https://sepoliafaucet.com/ - Yêu cầu đăng nhập Alchemy")
        print("2. https://sepolia-faucet.pk910.de/ - Faucet PoW (đào trên trình duyệt)")
        print("3. https://faucet.sepolia.dev/ - Faucet chính thức")
        print(f"\nĐịa chỉ ví của bạn: {address}")
        
        proceed = input("\nBạn có muốn tiếp tục không? (Nhập 'y' để tiếp tục): ")
        if proceed.lower() != 'y':
            print("Thoát chương trình.")
            return
    
    # Kiểm tra xem contract đã được biên dịch chưa
    if os.path.exists(COMPILED_PATH):
        print(f"\nĐã tìm thấy contract đã biên dịch tại {COMPILED_PATH}")
        with open(COMPILED_PATH, "r") as f:
            contract_interface = json.load(f)
    else:
        # Biên dịch contract
        contract_interface = compile_contract()
        if not contract_interface:
            print("Không thể tiếp tục do lỗi biên dịch.")
            return
    
    # Kiểm tra xem contract đã được triển khai chưa
    contract_address_file = os.path.join("build", "contract_address.txt")
    
    if os.path.exists(contract_address_file):
        with open(contract_address_file, "r") as f:
            contract_address = f.read().strip()
        print(f"\nContract đã được triển khai trước đó tại địa chỉ: {contract_address}")
        
        # Xác minh contract
        abi = contract_interface["abi"]
        verify_deployment(contract_address, abi)
    else:
        # Triển khai contract
        if balance_wei > 0:
            # Thông số khởi tạo cho SimpleToken
            constructor_args = ["MyToken", "MTK", 18, 1000000]  # Tên, ký hiệu, số thập phân, tổng cung
            
            contract_address, abi = deploy_contract(private_key, contract_interface, constructor_args)
            
            if contract_address and abi:
                # Xác minh contract
                verify_deployment(contract_address, abi)
            else:
                print("Không thể tiếp tục do lỗi triển khai.")
                return
        else:
            print("\nKhông thể triển khai contract do không có đủ ETH.")
            return
    
    # Tương tác với contract
    print("\n=== Menu Tương tác ===")
    print("1. Chuyển token đến địa chỉ khác")
    print("2. Thoát")
    
    choice = input("\nLựa chọn của bạn (1-2): ")
    
    if choice == "1":
        # Tạo ví thứ hai để nhận token
        second_private_key, second_address = create_account()
        
        # Số lượng token để chuyển
        amount = 100  # 100 token
        
        # Thực hiện chuyển token
        abi = contract_interface["abi"]
        interact_with_contract(contract_address, abi, private_key, second_address, amount)
    else:
        print("Thoát chương trình.")


if __name__ == "__main__":
    main() 