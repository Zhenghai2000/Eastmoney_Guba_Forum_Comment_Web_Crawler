import os
from tqdm import tqdm

ok_dir = "temporary_data"
tail_dir = "final_data"
error_dir = "error"


ok_codes = os.listdir(ok_dir)
tail_codes = []

years = ['2022','2021','2020','2019','2018','2017']
years.reverse()


for code in tqdm(ok_codes):
     with open(os.path.join(ok_dir,code),encoding='utf8') as f:
         lines = f.readlines()
         lines.reverse()
         for i in range(len(lines)):
             if lines[i][-17:-13] in years:
                 break
         if lines[i][-17:-13] != "2017":
             with open('error.txt','a') as f:
                 f.write(f'{code}\n')
                
         lines = lines[i:]
         lines.reverse()
         with open(os.path.join(tail_dir,code),"w+",encoding="utf8") as f:
             f.write("".join(lines))
                

with open('error.txt') as f:
    error_code = f.readlines()
    error_code = [i.strip() for i in error_code]
    
for code in tqdm(error_code):
    with open(os.path.join(tail_dir,code),encoding="utf8") as f:
        with open(os.path.join(error_dir,code),"w+",encoding="utf8") as ff:
            ff.write(f.read())
            
            
            
            
            
            
            
            
            
            
            
            
            
            
