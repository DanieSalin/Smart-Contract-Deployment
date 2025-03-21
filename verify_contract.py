#!/usr/bin/env python3
"""
Script để xác minh và tương tác với smart contract đã biên dịch
Cho phép kiểm tra smart contract mà không cần triển khai (vì không có ETH)
"""

import json
import os
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

# Đường dẫn đến file contract đã biên dịch
COMPILED_PATH = os.path.join("build", "SimpleToken.json")


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


def load_contract_abi():
    """Đọc ABI của contract từ file JSON"""
    try:
        with open(COMPILED_PATH, "r") as f:
            contract_interface = json.load(f)
        return contract_interface.get("abi")
    except FileNotFoundError:
        print(f"Không tìm thấy file {COMPILED_PATH}")
        return None


def verify_contract_abi():
    """Xác minh ABI của contract đã biên dịch"""
    print("\n=== Xác minh ABI của Smart Contract ===")
    
    abi = load_contract_abi()
    if not abi:
        print("Không thể tải ABI của contract")
        return False
    
    # Kiểm tra các hàm cần thiết cho token ERC-20
    required_functions = [
        "name", "symbol", "decimals", "totalSupply", "balanceOf", 
        "transfer", "transferFrom", "approve", "allowance"
    ]
    required_events = ["Transfer", "Approval"]
    
    # Lấy tất cả tên hàm và sự kiện từ ABI
    function_names = []
    event_names = []
    
    for item in abi:
        if item.get("type") == "function":
            function_names.append(item.get("name"))
        elif item.get("type") == "event":
            event_names.append(item.get("name"))
    
    # Kiểm tra các hàm cần thiết
    missing_functions = [fn for fn in required_functions if fn not in function_names]
    missing_events = [ev for ev in required_events if ev not in event_names]
    
    if missing_functions:
        print(f"Thiếu các hàm sau trong ABI: {missing_functions}")
        return False
    
    if missing_events:
        print(f"Thiếu các sự kiện sau trong ABI: {missing_events}")
        return False
    
    print("Contract tuân thủ tiêu chuẩn ERC-20 cơ bản")
    print(f"Số lượng hàm: {len(function_names)}")
    print(f"Các hàm trong contract: {', '.join(function_names)}")
    print(f"Các sự kiện trong contract: {', '.join(event_names)}")
    
    return True


def simulate_contract_deployment():
    """Mô phỏng triển khai contract để kiểm tra tính năng"""
    print("\n=== Mô phỏng triển khai Smart Contract ===")
    
    abi = load_contract_abi()
    if not abi:
        print("Không thể tải ABI của contract")
        return
    
    # Giả lập địa chỉ contract (địa chỉ không có thật trên mạng)
    fake_contract_address = "0x1234567890123456789012345678901234567890"
    print(f"Địa chỉ contract (giả lập): {fake_contract_address}")
    
    # Thông số token
    token_name = "MyToken"
    token_symbol = "MTK"
    token_decimals = 18
    token_total_supply = 1000000 * (10 ** token_decimals)  # 1 triệu token
    
    print(f"Thông tin token giả lập:")
    print(f"- Tên: {token_name}")
    print(f"- Ký hiệu: {token_symbol}")
    print(f"- Số thập phân: {token_decimals}")
    print(f"- Tổng cung: {token_total_supply / (10 ** token_decimals)} {token_symbol}")
    
    # Thông tin giao dịch triển khai
    print("\nQuy trình triển khai (mô phỏng):")
    print("1. Tạo giao dịch triển khai với constructor:")
    print(f"   - name: '{token_name}'")
    print(f"   - symbol: '{token_symbol}'")
    print(f"   - decimals: {token_decimals}")
    print(f"   - initialSupply: {1000000}")
    print("2. Ký giao dịch với private key")
    print("3. Gửi giao dịch đến mạng Sepolia")
    print("4. Đợi giao dịch được xác nhận (Block time trung bình 15 giây)")
    print("5. Nhận địa chỉ contract triển khai")
    
    # Hiển thị các hàm và sự kiện chính
    print("\nSau khi triển khai, contract sẽ có các hàm sau:")
    functions = ["name()", "symbol()", "decimals()", "totalSupply()", "balanceOf(address)", 
                "transfer(address,uint256)", "approve(address,uint256)", 
                "transferFrom(address,address,uint256)", "allowance(address,address)"]
    for func in functions:
        print(f"- {func}")
    
    print("\nSau khi triển khai, contract sẽ có các sự kiện sau:")
    events = ["Transfer(address indexed from, address indexed to, uint256 value)", 
             "Approval(address indexed owner, address indexed spender, uint256 value)"]
    for event in events:
        print(f"- {event}")
    
    print("\nGhi chú: Đây chỉ là mô phỏng để kiểm tra cấu trúc smart contract.")
    print("Khi triển khai thực tế, contract sẽ có địa chỉ riêng và các giá trị thực.")


def analyze_contract_bytecode():
    """Phân tích bytecode của contract"""
    print("\n=== Phân tích Bytecode của Smart Contract ===")
    
    try:
        with open(COMPILED_PATH, "r") as f:
            contract_interface = json.load(f)
        
        bytecode = contract_interface.get("bin")
        if not bytecode:
            print("Không tìm thấy bytecode trong file biên dịch")
            return
        
        bytecode_size = len(bytecode) // 2  # Mỗi byte là 2 ký tự hex
        
        print(f"Kích thước bytecode: {bytecode_size} byte")
        
        # Kiểm tra giới hạn bytecode của Ethereum (24KB)
        if bytecode_size > 24 * 1024:
            print("CẢNH BÁO: Bytecode vượt quá giới hạn 24KB của Ethereum")
        else:
            print(f"Bytecode trong giới hạn cho phép ({bytecode_size} / {24 * 1024} byte)")
        
        # Hiển thị một phần của bytecode
        print("\nPhần đầu bytecode:")
        print(bytecode[:100] + "...")
        
    except Exception as e:
        print(f"Lỗi khi phân tích bytecode: {e}")


def estimate_deployment_cost():
    """Ước tính chi phí triển khai contract"""
    print("\n=== Ước tính chi phí triển khai Smart Contract ===")
    
    try:
        with open(COMPILED_PATH, "r") as f:
            contract_interface = json.load(f)
        
        bytecode = contract_interface.get("bin")
        if not bytecode:
            print("Không tìm thấy bytecode trong file biên dịch")
            return
        
        # Lấy giá gas hiện tại
        gas_price_wei = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price_wei, "gwei")
        
        # Ước tính lượng gas cần thiết (bytecode_size * 200 gas là một ước tính thô)
        bytecode_size = len(bytecode) // 2
        estimated_gas = bytecode_size * 200
        
        # Thêm lượng gas cố định cho việc khởi tạo (khoảng 21000 gas)
        estimated_gas += 21000
        
        # Ước tính chi phí triển khai
        estimated_cost_wei = estimated_gas * gas_price_wei
        estimated_cost_eth = w3.from_wei(estimated_cost_wei, "ether")
        
        print(f"Giá gas hiện tại: {gas_price_gwei} Gwei")
        print(f"Ước tính lượng gas cần thiết: {estimated_gas}")
        print(f"Ước tính chi phí triển khai: {estimated_cost_eth} ETH")
        
        # Lưu ý về dự trữ ETH
        print("\nLưu ý: Bạn nên có lượng ETH nhiều hơn ước tính trên để đảm bảo đủ cho việc triển khai.")
        print("Thông thường, nên có ít nhất 0.1 ETH trong ví khi triển khai contract trên mạng thử nghiệm.")
        
        # Hiển thị các faucet để nhận ETH testnet
        print("\nCác faucet để nhận ETH testnet Sepolia:")
        print("1. https://sepoliafaucet.com/ - Yêu cầu đăng nhập Alchemy")
        print("2. https://sepolia-faucet.pk910.de/ - Faucet PoW (đào trên trình duyệt)")
        print("3. https://faucet.sepolia.dev/ - Faucet chính thức")
        
        _, address = load_account_info()
        if address:
            print(f"\nĐịa chỉ ví của bạn: {address}")
            
    except Exception as e:
        print(f"Lỗi khi ước tính chi phí triển khai: {e}")


def simulate_token_transfer():
    """Mô phỏng chuyển token từ một địa chỉ sang địa chỉ khác"""
    print("\n=== Mô phỏng chuyển Token ===")
    
    _, account_address = load_account_info()
    if not account_address:
        print("Không thể tải thông tin tài khoản")
        return
    
    # Tạo địa chỉ giả định để nhận token
    receiver = Account.create()
    receiver_address = receiver.address
    
    # Số lượng token để chuyển
    amount = 100  # 100 token
    
    print(f"Mô phỏng chuyển {amount} token:")
    print(f"Từ: {account_address}")
    print(f"Đến: {receiver_address}")
    
    print("\nQuá trình giao dịch (mô phỏng):")
    print("1. Kiểm tra số dư của người gửi")
    print("2. Giảm số dư của người gửi")
    print("3. Tăng số dư của người nhận")
    print("4. Phát ra sự kiện Transfer")
    
    print("\nGhi chú: Đây chỉ là mô phỏng và không thực hiện giao dịch thực tế trên blockchain.")


def main():
    print("=== KIỂM TRA SMART CONTRACT ERC-20 ===")
    
    # Tải thông tin tài khoản
    private_key, address = load_account_info()
    
    if not private_key or not address:
        print("Không tìm thấy thông tin tài khoản!")
        return
    
    print(f"\n=== Thông tin tài khoản ===")
    print(f"Địa chỉ: {address}")
    print(f"Private key: {private_key[:6]}...{private_key[-4:]}")
    
    # Kiểm tra xem contract đã được biên dịch chưa
    if not os.path.exists(COMPILED_PATH):
        print(f"\nKhông tìm thấy contract đã biên dịch tại {COMPILED_PATH}")
        print("Vui lòng chạy compile_deploy.py trước để biên dịch contract.")
        return
    
    print(f"\nĐã tìm thấy contract đã biên dịch tại {COMPILED_PATH}")
    
    while True:
        # Hiển thị menu
        print("\n=== Menu ===")
        print("1. Xác minh ABI của contract")
        print("2. Phân tích bytecode của contract")
        print("3. Ước tính chi phí triển khai")
        print("4. Mô phỏng triển khai contract")
        print("5. Mô phỏng chuyển token")
        print("0. Thoát")
        
        choice = input("\nLựa chọn của bạn (0-5): ")
        
        if choice == "1":
            verify_contract_abi()
        elif choice == "2":
            analyze_contract_bytecode()
        elif choice == "3":
            estimate_deployment_cost()
        elif choice == "4":
            simulate_contract_deployment()
        elif choice == "5":
            simulate_token_transfer()
        elif choice == "0":
            print("Thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn từ 0-5.")


if __name__ == "__main__":
    main() 