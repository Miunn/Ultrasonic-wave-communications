class Write_Pitaya_Socket:
    IP = '10.42.0.124'
    
    def __init__(self, ip='10.42.0.125'):
        self.IP = ip

    def connect(self):
        try:
            
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False