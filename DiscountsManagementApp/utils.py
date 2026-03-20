
def validate_registration_data(full_name, phone_number, password, confirm):
    if not full_name or not full_name.strip():
        return False, 'Họ và tên là bắt buộc!'
    if not phone_number or not phone_number.strip():
        return False, 'Số điện thoại là bắt buộc!'
    if not password:
        return False, 'Mật khẩu là bắt buộc!'
    if password != confirm:
        return False, 'Mật khẩu xác nhận không khớp!'
    return True, ''