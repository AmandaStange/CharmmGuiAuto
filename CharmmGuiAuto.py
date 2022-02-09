#!/usr/bin/env python
# coding: utf-8



import selenium
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
import time
import os
import sys
import yaml




class CharmmGuiAuto:
    def __init__(self, head, system):
        '''
        head = True or False, for True the browser window is not visible for the user
        system = membrane or solution
        '''
        #self.path_out = 
        options = webdriver.FirefoxOptions();
        #options.set_preference("browser.download.folderList", 2)
        #options.set_preference("browser.download.manager.showWhenStarting", False)
        #options.set_preference("browser.download.dir", self.path_out)
        #options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/gzip")
        #options.set_preference("browser.download.improvements_to_download_panel", True);
        #options.set_preference("browser.download.manager.closeWhenDone", True)
        options.headless = head
        self.driver = webdriver.Firefox(options=options)
        if system == 'membrane':
            self.driver.get('https://www.charmm-gui.org/?doc=input/membrane.bilayer')
        else:
            self.driver.get('https://charmm-gui.org/?doc=input/solution')
    
    def nxt(self):
        self.driver.find_element(By.ID, 'nextBtn').click()
    
    def login(self, email, password):
        self.driver.find_element(By.NAME, 'email').send_keys(email)
        self.driver.find_element(By.NAME, 'password').send_keys(password)
        self.driver.find_element(By.CLASS_NAME, 'loginbox').submit()
        
    def upload(self, file_name, path):
        '''
        file_name = the name of your pdb file with the .pdb extension
        path = the path to your file 
        '''
        choose_file = self.driver.find_element(By.NAME, 'file')
        file_location = os.path.join(path, file_name)
        choose_file.send_keys(file_location)
        self.driver.find_element(By.ID, 'nav_title').click()
        
    def wait_text(self,text,start_time=None):
        try:
            self.driver.window_handles
            if start_time == None:
                print(f'Waiting for: {text}')
                start_time = time.time()
            else:
                print(f'Still waiting for: {text} (time elapsed {(time.time() - start_time)/60:.2f} minutes)')
            try:
                wait = WebDriverWait(self.driver, 300)
                element = wait.until(EC.text_to_be_present_in_element((By.ID, "body"), text))
                print('Found it!')
            except:
                try:
                    WebDriverWait(self.driver, 1).until(EC.text_to_be_present_in_element((By.ID, "error_msg"), "CHARMM was terminated abnormally"))
                    print('ERROR MESSAGE - check "screenshot_error.png"')
                    self.driver.save_screenshot("screenshot_error.png")
                    self.driver.quit()
                except:
                    self.wait_text(text, start_time)
        except:
            print('window has been closed')
            self.driver.quit()

            
        
    def patch(self, chain, ter, ter_patch):
        Select(self.driver.find_element(By.NAME, f'terminal[{chain}][{ter}]')).select_by_value(f'{ter_patch}')

    def waterbox(self, size='implicit', shape = 'rect', dis=10.0, X=10.0, Y=10.0, Z=10.0):
        '''
        size = 'explicit' or 'implicit'
        shape = 'rect' or 'octa'
        '''
        if size == 'explicit':
            self.driver.find_element(By.XPATH, '//*[@id="fsolution"]/div[1]/table/tbody/tr[1]/td[1]/input').click()
            if shape == 'rect':
                Select(self.driver.find_element(By.NAME, 'solvtype')).select_by_value('rect')
                self.driver.find_element(By.XPATH, '//*[@id="box[rect][x]"]').send_keys(X)
                self.driver.find_element(By.XPATH, '//*[@id="box[rect][y]"]').send_keys(Y)
                self.driver.find_element(By.XPATH, '//*[@id="box[rect][z]"]').send_keys(Z)
            else:
                Select(self.driver.find_element(By.NAME, 'solvtype')).select_by_value('octa')
                self.driver.find_element(By.XPATH, '//*[@id="box[octa][x]"]').send_keys(X)
        else:
            self.driver.find_element(By.XPATH, '//*[@id="fsolution"]/div[1]/table/tbody/tr[2]/td[1]/input').click()
            if shape == 'rect':
                Select(self.driver.find_element(By.NAME, 'solvtype')).select_by_value('rect')
            else:
                Select(self.driver.find_element(By.NAME, 'solvtype')).select_by_value('octa')
            if dis != 10.0:
                edge = self.driver.find_element(By.XPATH, '//*[@id="fitedge"]')
                edge.clear()
                edge.send_keys(dis)
        
    def ion_method(self, method=None):
        '''
        method = 'mc' or 'dist'
        '''
        if method == None:
            return
        Select(self.driver.find_element(By.NAME, 'ion_method')).select_by_value(method)

    def clear_ion(self):
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.XPATH, '//*[@id="ions_table"]/tbody/tr/td[6]/input').click()

    def add_ion(self,formula, conc=0.15, neu=True):
        '''
        formular = 'KCl', 'NaCl', 'CaCl2' or 'MgCl2'
        '''
        Select(self.driver.find_element(By.ID, 'ion_type')).select_by_value(formula)
        self.driver.find_element(By.XPATH, '//*[@id="simple_ions_widget"]/input').click()
        if conc != 0.15:
            c = self.driver.find_element(By.XPATH, '//*[@id="ions_table"]/tbody/tr[1]/td[4]/input')
            c.clear()
            c.send_keys(conc)
        if not neu:
            self.driver.find_element(By.XPATH, '//*[@id="ions_table"]/tbody/tr[1]/td[5]/input').click()
    
    def calc_solv(self):
        self.driver.find_element(By.XPATH, '//*[@id="fsolution"]/div[6]/input').click()
        
    def force_field(self, ff):
        '''
        ff = 'c36m', 'c36', 'amber' or 'opls'
        '''
        Select(self.driver.find_element(By.NAME, 'fftype')).select_by_value(ff)

    
    def engine(self,software):
        '''
        software = 'namd'(NAMD), 'gmx'(GROMACS), 'amb'(AMBER), 'omm'(OpenMM), 
                    'comm'(CHARMM/OpenMM), 'gns'(GENESIS), 'dms'(Desmond), 
                    'lammps', or 'tinker'
        '''
        self.driver.find_element(By.XPATH, f'//*[@id="input_{software}"]/td/input').click()

    def temperature(self,temp=303.15):
        if temp!= 303.15:
            t = self.driver.find_element(By.NAME, 'temperature')
            t.clear()
            t.send_keys(temp)




class SolutionProtein(CharmmGuiAuto):
    def run(self, email, password, file_name, path, chains = None, ions='NaCl', ff='c36m', engine='gmx', temp='310', waterbox={'dis': 15.0}, ion_method=None):
        self.login(email,password)
        self.wait_text("Protein Solution System")
        self.upload(file_name, path)
        self.wait_text("Model/Chain Selection Option")
        jobid = self.driver.find_element(By.CLASS_NAME, "jobid").text
        print(jobid)
        self.nxt()
        self.wait_text("PDB Manipulation Options")
        if chains != None:
            for chain in chains:
                self.patch(chain[0], chain[1], chain[2])
        self.nxt()
        self.wait_text("Add Ions")
        self.waterbox(**waterbox)
        self.ion_method(ion_method)
        self.clear_ion()
        self.add_ion(ions)
        self.calc_solv()
        self.nxt()
        self.wait_text('Periodic Boundary Condition Options')
        self.nxt()
        self.wait_text("Force Field Options")
        self.force_field(ff)
        self.engine(engine)
        self.temperature(temp)
        self.nxt()
        self.wait_text("to continue equilibration and production simulations")
        print(f'Ready to download from retrive job id {jobid}')
        self.driver.quit()




class MembraneProtein(CharmmGuiAuto):
    '''
    find lipid names https://www.charmm-gui.org/?doc=archive&lib=lipid (file name is the same as lipid name)
    '''
    def orientation(self, option='PDB', first_point=None, second_point=None,unchecked=None):
        '''
        PDB: Use PDB Orientation
        Principal: Align the First Principal Axis Along Z
        Vector: Align a Vector (Two Atoms) Along Z
        PPM: Use PPM Server
        For Vector:
        first_point: a list of chain name, residue name and residue index of the first point of the vector (ie. ['PROA', 'HIS', 1])
        second_point: a list of chain name, residue name and residue index of the second point of the vector
        For PPM:
        Unchecked: list of chain names that should NOT be sent to the server (ie ['PROA'] or ['PROA', 'PROB'])
        '''
        o = ['PDB', 'Principal', 'Vector', 'PPM'].index(option)
        self.driver.find_elements(By.NAME, 'align_option')[o].click()

        if o == 2:

            for j,point in enumerate([first_point, second_point]):
                self.driver.find_element(By.ID, f'align[{j}][segid]').clear()
                self.driver.find_element(By.ID, f'align[{j}][segid]').send_keys(point[0])
                self.driver.find_element(By.ID, f'align[{j}][residue]').clear()
                self.driver.find_element(By.ID, f'align[{j}][residue]').send_keys(point[1])
                self.driver.find_element(By.ID, f'align[{j}][resid]').clear()
                self.driver.find_element(By.ID, f'align[{j}][resid]').send_keys(point[2])
        if o == 3 and unchecked != None:
            for j in unchecked:
                self.driver.find_element(By.NAME, f'ppm_chains[{j}]').click()


    def position(self, option=None,value=None):
        '''
        X: rotate_x_checked + rxdeg
        Y: rotate_y_checked + rydeg
        Z: translate_checked + zdist
        flip: flip_checked
        '''
        print(option)
        if option == None:
            return
        options = {'X': 'rotate_x_checked', 'Y': 'rotate_y_checked', 'Z': 'translate_checked', 'flip':'flip_checked'}
        self.driver.find_element(By.NAME, options[option]).click()
        if option != 'flip':
            values = {'X': 'rxdeg', 'Y': 'rydeg', 'Z': 'zdist'}
            self.driver.find_element(By.NAME, values[option]).clear()
            self.driver.find_element(By.NAME, values[option]).send_keys(value)

    def area(self, option=None, radius=None):
        if option == None:
            return
        self.driver.find_element(By.NAME, 'fill_checked').click()
        if option != 'rot':
            self.driver.find_elements(By.NAME, 'filltype')[1].click()
            self.driver.find_element(By.NAME, 'crad').send_keys(radius)
            
            
    def projection(self, option=None):
        '''
        option: upper or lower
        '''
        if option == None:
            return
        self.driver.find_element(By.NAME, f'prot_projection_{option}').click()

    def box_type(self, option=None):
        '''
        rect or hexa
        '''
        if option == None:
            return
        Select(self.driver.find_element(By.NAME, 'hetero_boxtype')).select_by_value(option)

    def lengthZ(self, option=None,value=None):
        '''
        option: wdist of nhydration
        '''
        if option == None:
            return
        o = ['wdist','nhydration'].index(option)
        default = [(22.5, 'hetero_wdist'), (50, 'hetero_nhydration')]
        if value == None:
            value = default[o][0]
        self.driver.find_elements(By.NAME,'hetero_z_option')[o].click()
        self.driver.find_element(By.NAME, default[o][1]).clear()
        self.driver.find_element(By.NAME, default[o][1]).send_keys(value)

    def lengthXY(self, option=None,value=None):
        '''
        option: ratio or nlipid
        '''
        if option == None:
            return
        options = {'ratio':'hetero_lx', 'nlipid':'hetero_xvsy'} 
        if option == 'nlipid':
            self.driver.find_elements(By.NAME, 'hetero_xy_option')[1].click()
        self.driver.find_element(By.NAME, options[option]).clear()
        self.driver.find_element(By.NAME, options[option]).send_keys(value)

    def add_lipid(self, lipid, upper, lower):
        '''
        OPS: N-acylated Amino acids, PEG Lipids, and Glycolipids must be added using their respective functions (add_naa, add_peg, and add_glycolipid)
        as these have many different options that are not applicable to the rest of the lipids
        '''
        buttons = self.driver.find_elements(By.XPATH,"//img[contains(@src,'tri.png')]")
        if len(buttons) != 0:
            [x.click() for x in buttons if x.is_displayed()]
        u = self.driver.find_element(By.NAME, f'lipid_ratio[upper][{lipid}]')
        u.clear()
        u.send_keys(upper)
        l = self.driver.find_element(By.NAME, f'lipid_ratio[lower][{lipid}]')
        l.clear()
        l.send_keys(lower)

    def show_system_info(self):
        self.driver.find_element(By.ID,'hetero_size_button').click()
        time.sleep(1)        
    
    def add_naa(self, lipid='LAU', aa='GLY', cter='CTER', lower=1,upper=1):
        prevs = [i.get_attribute('value') for i in self.driver.find_elements(By.XPATH, '//input[starts-with(@value, "NAA")]')]
        if len(prevs) != 0:
            prev = sorted(set(prevs))[-1][-1]
            new = chr(ord(prev)+1).upper()
        else:
            new = 'A'
        new_l = new.lower()
        self.driver.find_element(By.ID, 'add_ratio_nacylaa').click()
        main_window = self.driver.window_handles[0]
        self.driver.find_element(By.XPATH, f"//input[@value=\"NAA{new}\"]").click()
        popup = self.driver.window_handles[-1]
        self.driver.switch_to.window(popup)
        time.sleep(0.5)
        Select(self.driver.find_element(By.ID, f'nacylaa_lipid')).select_by_value(lipid)
        Select(self.driver.find_element(By.ID, f'nacylaa_aa')).select_by_value(aa)
        Select(self.driver.find_element(By.ID, f'nacylaa_cter')).select_by_value(cter)
        self.nxt()
        self.driver.switch_to.window(main_window)
        u = self.driver.find_element(By.NAME, f'lipid_ratio[upper][naa{new_l}]')
        u.clear()
        u.send_keys(upper)
        l = self.driver.find_element(By.NAME, f'lipid_ratio[lower][naa{new_l}]')
        l.clear()
        l.send_keys(lower)
        
    def add_peg(self, lipid='DAG', tail='DLGL', units=5, lower=1,upper=1):
        prevs = [i.get_attribute('value') for i in self.driver.find_elements(By.XPATH, '//input[starts-with(@value, "PEG")]')]
        if len(prevs) != 0:
            prev = sorted(set(prevs))[-1][-1]
            new = chr(ord(prev)+1).upper()
        else:
            new = 'A'
        new_l = new.lower()
        self.driver.find_element(By.ID, 'add_ratio_peg').click()
        main_window = self.driver.window_handles[0]
        self.driver.find_element(By.XPATH, f"//input[@value=\"PEG{new}\"]").click()
        popup = self.driver.window_handles[-1]
        self.driver.switch_to.window(popup)
        time.sleep(0.5)
        Select(self.driver.find_element(By.ID, f'peg_ltype')).select_by_value(lipid)
        Select(self.driver.find_element(By.ID, f'peg_lipid')).select_by_value(tail)
        u = self.driver.find_element(By.ID, f'peg_nunit')
        u.clear()
        u.send_keys(units)
        self.nxt()
        self.driver.switch_to.window(main_window)
        u = self.driver.find_element(By.NAME, f'lipid_ratio[upper][peg{new_l}]')
        u.clear()
        u.send_keys(upper)
        l = self.driver.find_element(By.NAME, f'lipid_ratio[lower][peg{new_l}]')
        l.clear()
        l.send_keys(lower)

        
        
    def sugar_options(self, sugar_id=1,link=None,ltype='B', sname='GLC'):
        Select(self.driver.find_element(By.ID, f'seq_name_{sugar_id}')).select_by_value(sname)
        Select(self.driver.find_element(By.ID, f'seq_type_{sugar_id}')).select_by_value(ltype)
        if link != None:
            Select(self.driver.find_element(By.ID, f'seq_link_{sugar_id}')).select_by_value(str(link))



    def add_sugar(self, sid='1'):
        self.driver.find_element(By.ID, sid).find_element(By.CLASS_NAME, 'add').click()


    def add_modification(self, sname= None, sugar_id = None, mod=None):
        '''
        add check to see if chem_checked is checked
        '''
        if mod == None:
            return
        if not self.driver.find_element(By.XPATH, '//input[@value="Add chemical modification"]').is_displayed():
            self.driver.find_element(By.ID, 'chem_checked').click()
        else:
            dself.river.find_element(By.XPATH, '//input[@value="Add chemical modification"]').click()
        resids = [i.get_attribute('id') for i in self.driver.find_elements(By.XPATH, '//select[starts-with(@id,"chem_res_")]') if i.is_displayed()]
        resid = resids[-1][-1]
        Select(self.driver.find_element(By.ID, f'chem_res_{resid}')).select_by_value(sname)
        Select(self.driver.find_element(By.ID, f'chem_resid_{resid}')).select_by_value(str(sugar_id))
        Select(self.driver.find_element(By.ID, f'chem_site_{resid}')).select_by_value(mod[0])
        Select(self.driver.find_element(By.ID, f'chem_patch_{resid}')).select_by_value(mod[1:])

    def add_glycolipid(self, GRS, upper=1, lower=1):
        prevs = [i.get_attribute('value') for i in self.driver.find_elements(By.XPATH, '//input[starts-with(@value, "GLP")]')]
        if len(prevs) != 0:
            prev = sorted(set(prevs))[-1][-1]
            new = chr(ord(prev)+1).upper()
        else:
            new = 'A'
        new_l = new.lower()
        self.driver.find_element(By.ID, 'add_ratio_gl').click()
        main_window = self.driver.window_handles[0]
        self.driver.find_element(By.XPATH, f"//input[@value=\"GLP{new}\"]").click()
        popup = self.driver.window_handles[-1]
        self.driver.switch_to.window(popup)
        time.sleep(2)

        lipids_dict = {'CER': 'CER', 'PIC': 'PICER', 'DAG': 'DAG', 'PID': 'PIDAG', 'ACYL':'ACYL'}

        sugars_dict = {}
        branch_length = [(1,1)]
        ## Making the sugar dictionary ##
        for i in GRS.split('\n'):
            sug = i.split(' ')
            if len(sug) > 2:
                if '_' in sug[-1]:
                    sug = sug[:-1] + sug[-1].split('_')
                else:
                    sug += [None]
                sugars_dict[int(sug[0])] = {'sname': sug[-2][1:], 'sugar_id': int(sug[0])-1, 'ltype': sug[-2][0], 'mod': sug[-1]} 
                if  sugars_dict[int(sug[0])]['sugar_id'] != 1:
                    sugars_dict[int(sug[0])]['link'] =  sug[-3][1]
                    if len(sug) > 1:
                        for j in branch_length[::-1]:
                            if len(sug)-3 > j[1]:
                                branch_length.append((int(sug[0])-1, len(sug)-3))
                                sugars_dict[int(sug[0])]['branch'] = j[0]
                                break
            if len(sug) == 2:
                sugars_dict[int(sug[0])] = {'lipid_type': lipids_dict[sug[-1].replace('-','')[:3]],'lipid_tail': sug[-1]}


        # Adding the sugars ##
        for i in range(1,1+len(sugars_dict)):
            if i == 1:
                Select(self.driver.find_element(By.ID, 'lipid_types')).select_by_value(sugars_dict[i]['lipid_type'])
                Select(self.driver.find_element(By.ID, 'seq_name_0')).select_by_value(sugars_dict[i]['lipid_tail'])
            elif i == 2:
                self.sugar_options(sugar_id = sugars_dict[i]['sugar_id'], link = sugars_dict[i].get('link', None), ltype = sugars_dict[i]['ltype'], sname =sugars_dict[i]['sname'])
                self.add_modification(sname= sugars_dict[i]['sname'], sugar_id = sugars_dict[i]['sugar_id'], mod=sugars_dict[i]['mod'])
            else:
                self.add_sugar(sugars_dict[i]['branch'])
                self.sugar_options(sugar_id = sugars_dict[i]['sugar_id'], link = sugars_dict[i].get('link', None), ltype = sugars_dict[i]['ltype'], sname =sugars_dict[i]['sname'])
                self.add_modification(sname= sugars_dict[i]['sname'], sugar_id = sugars_dict[i]['sugar_id'], mod=sugars_dict[i]['mod'])

        self.nxt()
        self.driver.switch_to.window(main_window)
        u = self.driver.find_element(By.NAME, f'lipid_ratio[upper][glp{new_l}]')
        u.clear()
        u.send_keys(upper)
        l = self.driver.find_element(By.NAME, f'lipid_ratio[lower][glp{new_l}]')
        l.clear()
        l.send_keys(lower)
        
        

    def run(self, email, password, file_name, path, chains = None, orientation = 'PDB', position = None, area=None, projection = None, boxtype=None, lengthZ=None, lipids = None, naas = None, pegs = None, glycolipids = None, size = 100, ions='NaCl', ff='c36m', engine='gmx', temp='310'):
        self.login(email,password)
        self.wait_text("Protein/Membrane System")
        self.upload(file_name, path)
        self.wait_text("Model/Chain Selection Option")
        jobid = self.driver.find_element(By.CLASS_NAME, "jobid").text
        print(jobid)
        self.nxt()
        self.wait_text("PDB Manipulation Options")
        if chains != None:
            for chain in chains:
                self.patch(chain[0], chain[1], chain[2])
        self.nxt()
        self.wait_text("Area Calculation Options")
        self.orientation(**orientation)
        self.position(**position)
        self.area(**area)
        self.nxt()
        self.wait_text('default surface area')
        self.projection(**projection)
        self.box_type(**boxtype)
        self.lengthZ(**lengthZ)
        self.lengthXY('ratio', size)
        if lipids != None:
            for lipid in lipids:
                self.add_lipid(lipid[0], lipid[1], lipid[2])
        if naas != None:
            for naa in naas:
                self.add_naa(naa[0], naa[1], naa[2], naa[3], naa[4])
        if pegs != None:
            for peg in pegs:
                self.add_peg(peg[0], peg[1], peg[2], peg[3], peg[4])
        if glycolipids != None:
            for glycolipid in glycolipids:
                #self.add_glycolipid(glycolipid[0], glycolipid[1], glycolipid[2])
                self.add_glycolipid(glycolipid['GRS'], glycolipid['upper'], glycolipid['lower'])
        self.show_system_info()
        self.wait_text('Calculated XY System Size')
        self.nxt()
        self.wait_text("Component Building Options")
        self.clear_ion()
        self.add_ion('NaCl')
        self.driver.find_element(By.XPATH, "//*[starts-with(@onclick, 'update_nion')]").click()
        self.nxt()
        self.wait_text('Building Ion and Waterbox')
        self.nxt()
        self.wait_text('Assemble Generated Components')
        self.nxt()
        self.wait_text("Force Field Options")
        self.force_field(ff)
        self.engine(engine)
        self.temperature(temp)
        self.nxt()
        self.wait_text("to continue equilibration and production simulations")
        print(f'Ready to download from retrive job id {jobid}')




class Membrane(MembraneProtein):
    '''
    find lipid names https://www.charmm-gui.org/?doc=archive&lib=lipid (file name is the same as lipid name)
    '''
    
    def run(self, email, password, boxtype=None, lengthZ=None, lipids = None, naas = None, pegs = None, glycolipids = None, size = 100, ions='NaCl', ff='c36m', engine='gmx', temp='310'):
        self.login(email,password)
        self.wait_text("Protein/Membrane System")
        self.driver.find_element(By.XPATH, '//a[@href="#"]').click()
        #self.driver.find_element(By.ID, 'nav_title').click()
        self.wait_text('default surface area')
        jobid = self.driver.find_element(By.CLASS_NAME, "jobid").text
        print(jobid)
        self.lengthXY('ratio', size)
        if lipids != None:
            for lipid in lipids:
                self.add_lipid(lipid[0], lipid[1], lipid[2])
        if naas != None:
            for naa in naas:
                self.add_naa(naa[0], naa[1], naa[2], naa[3], naa[4])
        if pegs != None:
            for peg in pegs:
                self.add_peg(peg[0], peg[1], peg[2], peg[3], peg[4])
        if glycolipids != None:
            for glycolipid in glycolipids:
                #self.add_glycolipid(glycolipid[0], glycolipid[1], glycolipid[2])
                self.add_glycolipid(glycolipid['GRS'], glycolipid['upper'], glycolipid['lower'])        
        self.show_system_info()
        self.wait_text('Calculated XY System Size')
        self.nxt()
        self.wait_text("Component Building Options")
        self.clear_ion()
        self.add_ion('NaCl')
        self.driver.find_element(By.XPATH, "//*[starts-with(@onclick, 'update_nion')]").click()
        self.nxt()
        self.wait_text('Building Ion and Waterbox')
        self.nxt()
        self.wait_text('Assemble Generated Components')
        self.nxt()
        self.wait_text("Force Field Options")
        self.force_field(ff)
        self.engine(engine)
        self.temperature(temp)
        self.nxt()
        self.wait_text("Equilibration Input Notes")
        print(f'Ready to download from retrive job id {jobid}')
        self.driver.quit()




def main(system_type):
    if system_type == 'SP':
        SolutionProtein(**parsed_yaml['input1']).run(**parsed_yaml['input2'])
    elif system_type == 'MP':
        MembraneProtein(**parsed_yaml['input1']).run(**parsed_yaml['input2'])
    elif system_type == 'M':
        Membrane(**parsed_yaml['input1']).run(**parsed_yaml['input2'])
    else:
        print('System type must be specified')

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str,
                    help='The name of the input yaml file without the extension')
args = parser.parse_args()



if __name__ == "__main__":
    with open(f'{args.input_file}.yaml', 'r') as stream:
        parsed_yaml=yaml.safe_load(stream)
        print(parsed_yaml)
    main(**parsed_yaml['input0'])
