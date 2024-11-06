

def txt2it(txt_path, it_file_path, eph_file_path, att_file_path):

    it_file = open(it_file_path, 'w')
    eph_file = open(eph_file_path, 'w')
    att_file = open(att_file_path, 'w')
    with open(txt_path, 'r') as f:
        gps_time = 0
        att_time = 0
        lines = f.readlines()
        line_num = 0.0
        for line in lines:
            dat = line.split('\t')
            if len(dat) == 20:
                it_file.write(f"{line_num}\t{dat[0]}\n{line_num + 1}\t{dat[1]}\n{line_num + 2}\t{dat[2]}\n{line_num + 3}\t{dat[3]}\n" 
                                f"{line_num + 4}\t{dat[4]}\n{line_num + 5}\t{dat[5]}\n{line_num + 6}\t{dat[6]}\n{line_num + 7}\t{dat[7]}\n")
                if float(dat[8]) != gps_time and len(dat) == 20:
                    eph_file.write(f"{dat[8]}\t{dat[9]}\t{dat[10]}\t{dat[11]}\t{dat[12]}\t{dat[13]}\t{dat[14]}\n")
                gps_time = float(dat[8])
                if dat[15] != att_time and len(dat) == 20:
                    att_file.write(f"{dat[15]}\t {dat[16]}\t {dat[17]}\t {dat[18]}\t {dat[19]}")
                att_time = dat[15]
                line_num += 8
                it_file.flush()
                eph_file.flush()
            else:
                print("error:", line_num)
        it_file.close()
    

            
            
if __name__=='__main__':
    txt_path = './data/aux_cmos1_pan_dingbiao.txt'
    it_file_path = './data/dingbiao.it'
    eph_file_path = './data/dingbiao.eph'
    att_file_path = './data/dingbiao.att'
    txt2it(txt_path=txt_path, it_file_path=it_file_path, eph_file_path=eph_file_path, 
            att_file_path=att_file_path)