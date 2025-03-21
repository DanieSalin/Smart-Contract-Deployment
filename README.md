# Triển khai Smart Contract Ethereum

Project này chứa các script để biên dịch, triển khai và tương tác với smart contract Ethereum sử dụng Python.

## Cấu trúc thư mục

```
├── src/                  # Thư mục chứa các file Solidity
│   └── SimpleToken.sol   # Smart contract token ERC-20 đơn giản
├── build/                # Thư mục chứa kết quả biên dịch và thông tin triển khai
├── compile_deploy.py     # Script chính để biên dịch và triển khai contract
└── README.md             # File hướng dẫn
```

## Yêu cầu

- Python 3.8+
- Web3.py
- py-solc-x (để biên dịch Solidity)

## Cài đặt

```bash
pip install web3 py-solc-x
```

## Các bước thực hiện

### 1. Biên dịch Smart Contract Solidity

Script Python sẽ tự động:
- Cài đặt trình biên dịch Solidity phiên bản 0.8.19
- Biên dịch file SimpleToken.sol 
- Lưu ABI và bytecode vào thư mục build/

### 2. Triển khai Smart Contract

Để triển khai smart contract, script sẽ:
- Tạo một tài khoản Ethereum mới (nếu chưa có)
- Lưu thông tin tài khoản vào file JSON trong thư mục build/
- Kiểm tra số dư ETH của tài khoản
- Triển khai contract lên mạng Sepolia
- Lưu địa chỉ contract đã triển khai vào file

### 3. Tương tác với Smart Contract

Sau khi triển khai, bạn có thể tương tác với contract thông qua các tính năng:
- Xem thông tin của token (tên, ký hiệu, số thập phân, tổng cung)
- Chuyển token đến địa chỉ khác
- Kiểm tra số dư token

## Cách sử dụng

Chạy script chính:

```bash
python compile_deploy.py
```

Script sẽ hướng dẫn bạn qua các bước tiếp theo. Lưu ý:

1. Bạn cần có ETH trên mạng Sepolia để triển khai và tương tác với contract. Bạn có thể nhận ETH miễn phí từ các faucet được đề xuất trong script.

2. KHÔNG BAO GIỜ sử dụng tài khoản chứa tài sản thật hoặc tiết lộ private key của bạn.

3. Script này chỉ nên được sử dụng trên mạng thử nghiệm (testnet) Sepolia.

## Chi tiết Smart Contract (SimpleToken.sol)

Smart contract `SimpleToken.sol` là một token ERC-20 đơn giản với các chức năng sau:

- Khởi tạo token với tên, ký hiệu, số thập phân và tổng cung
- Chuyển token giữa các địa chỉ (`transfer`)
- Ủy quyền cho địa chỉ khác chi tiêu token thay mặt bạn (`approve`)
- Chuyển token từ người được ủy quyền (`transferFrom`)
- Kiểm tra số dư token (`balanceOf`)

## Lưu ý

- Đây là project dành cho mục đích học tập và thử nghiệm.
- Luôn sử dụng mạng thử nghiệm (testnet) Sepolia, không sử dụng trên mạng chính (mainnet).
- Bảo vệ private key của bạn và không bao giờ chia sẻ chúng. 