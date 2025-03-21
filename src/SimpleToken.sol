// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SimpleToken
 * @dev Token ERC-20 đơn giản cho mục đích học tập
 */
contract SimpleToken {
    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    /**
     * @dev Khởi tạo hợp đồng với các thông số cụ thể
     * @param _name Tên của token
     * @param _symbol Ký hiệu của token
     * @param _decimals Số chữ số thập phân
     * @param _initialSupply Tổng cung ban đầu
     */
    constructor(
        string memory _name,
        string memory _symbol,
        uint8 _decimals,
        uint256 _initialSupply
    ) {
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        
        // Chuyển đổi tổng cung thành đơn vị token nhỏ nhất (wei)
        totalSupply = _initialSupply * (10 ** uint256(_decimals));
        
        // Cấp toàn bộ token cho người tạo hợp đồng
        balanceOf[msg.sender] = totalSupply;
        
        emit Transfer(address(0), msg.sender, totalSupply);
    }
    
    /**
     * @dev Thực hiện chuyển token từ người gọi đến địa chỉ nhận
     * @param _to Địa chỉ người nhận
     * @param _value Số lượng token để chuyển
     * @return Trả về true nếu chuyển thành công
     */
    function transfer(address _to, uint256 _value) public returns (bool) {
        require(_to != address(0), "Transfer to the zero address");
        require(balanceOf[msg.sender] >= _value, "Insufficient balance");
        
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        
        emit Transfer(msg.sender, _to, _value);
        return true;
    }
    
    /**
     * @dev Cho phép địa chỉ spender chi tiêu một số lượng token nhất định thay mặt cho người gọi
     * @param _spender Địa chỉ được ủy quyền chi tiêu
     * @param _value Số lượng token được phép chi tiêu
     * @return Trả về true nếu thành công
     */
    function approve(address _spender, uint256 _value) public returns (bool) {
        require(_spender != address(0), "Approve to the zero address");
        
        allowance[msg.sender][_spender] = _value;
        
        emit Approval(msg.sender, _spender, _value);
        return true;
    }
    
    /**
     * @dev Chuyển token từ địa chỉ _from đến địa chỉ _to, sử dụng cơ chế ủy quyền
     * @param _from Địa chỉ nguồn
     * @param _to Địa chỉ đích
     * @param _value Số lượng token để chuyển
     * @return Trả về true nếu chuyển thành công
     */
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
        require(_from != address(0), "Transfer from the zero address");
        require(_to != address(0), "Transfer to the zero address");
        require(balanceOf[_from] >= _value, "Insufficient balance");
        require(allowance[_from][msg.sender] >= _value, "Insufficient allowance");
        
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        allowance[_from][msg.sender] -= _value;
        
        emit Transfer(_from, _to, _value);
        return true;
    }
} 