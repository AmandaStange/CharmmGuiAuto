#!/usr/bin/env python
# coding: utf-8

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import yaml
import argparse
import random
import string
import traceback
import subprocess

class CharmmGuiAuto:
    def __init__(self, system, headless=True, path_out=None):
        """
        Initializes the CharmmGuiAuto class.

        Parameters:
            headless (bool): Whether to run the browser in headless mode.
            system (str): Type of system to set up ('membrane', 'solution', 'retrieve', 'reader', 'readerconverter', 'converter').
            path_out (str): Path to the output directory.
        """
        global out_tmp

        print(headless)

        options = webdriver.FirefoxOptions();

        if path_out is not None:
            letters = string.ascii_letters
            self.path_out = path_out
            out_tmp = f'{path_out}{"".join(random.choice(letters) for i in range(10))}'
            print(out_tmp)
            options.set_preference("browser.download.dir", out_tmp)

        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/gzip")
        options.set_preference("browser.download.improvements_to_download_panel", True)
        options.set_preference("browser.download.manager.closeWhenDone", True)
        #options.headless = True
        if headless is True:
            options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)
        if system == 'membrane':
            self.driver.get('https://www.charmm-gui.org/?doc=input/membrane.bilayer')
        elif system == 'solution':
            self.driver.get('https://charmm-gui.org/?doc=input/solution')
        elif system == 'retrieve':
            self.driver.get('https://www.charmm-gui.org/?doc=input/retriever')
        elif system in ['reader', 'readerconverter']:
            self.driver.get('https://www.charmm-gui.org/?doc=input/pdbreader')
        elif system == 'converter':
            self.driver.get('https://www.charmm-gui.org/?doc=input/converter.ffconverter')

    def take_full_page_screenshot(self, file_path, jobid):
            os.system(f'mkdir -p {self.path_out}/Screenshots/')
            # Set the viewport to the full height of the page
            scroll_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            self.driver.set_window_size(1920, scroll_height+75)  # Set width and height for full-page capture

            # Take and save the screenshot
            self.driver.save_screenshot(f'{self.path_out}/Screenshots/' + jobid.split()[2] + '_' + file_path)
            print(file_path)

    def nxt(self, prev_step=None, screen=False, jobid=None):
        """
        Presses the 'Next' button on the current page.
        """
        if screen:
            self.take_full_page_screenshot(file_path=f"{prev_step.replace(' ', '_')}.png", jobid=jobid)

        self.driver.find_element(By.ID, 'nextBtn').click()

    def login(self, email, password):
        """
        Logs into CHARMM-GUI using provided email and password.

        Parameters:
            email (str): User's email address.
            password (str): User's password.
        """
        self.driver.find_element(By.NAME, 'email').send_keys(email)
        self.driver.find_element(By.NAME, 'password').send_keys(password)
        self.driver.find_element(By.CLASS_NAME, 'loginbox').submit()

    def upload(self, file_name, path):
        """
        Uploads a local PDB file to CHARMM-GUI.

        Parameters:
            file_name (str): Name of the PDB file.
            path (str): Directory path where the PDB file is located.
        """
        choose_file = self.driver.find_element(By.NAME, 'file')
        file_location = os.path.join(path, file_name)
        choose_file.send_keys(file_location)
        try:
            self.driver.find_element(By.ID, 'nav_title').click()
        except:
            self.nxt()

    def from_pdb(self, pdb_id):
        """
        Fetches a PDB file from CHARMM-GUI using its PDB ID.

        Parameters:
            pdb_id (str): The PDB ID of the file to fetch.
        """
        self.driver.find_element(By.NAME, 'pdb_id').send_keys(pdb_id)
        try:
            self.driver.find_element(By.ID, 'nav_title').click()
        except:
            self.nxt()

    def wait_text(self, text, text2=None, start_time=None):
        """
        Waits until the specified text is visible on the page.

        Parameters:
            text (str): The text to wait for.
            start_time (float): The starting time for waiting (optional).
        """
        try:
            self.driver.window_handles
            if start_time is None:
                print(f'Waiting for: {text}')
                start_time = time.time()
            else:
                print(f'Still waiting for: {text} (time elapsed {(time.time() - start_time)/60:.2f} minutes)')
            try:
                wait = WebDriverWait(self.driver, 300)
                element = wait.until(EC.text_to_be_present_in_element((By.ID, "body"), text))
                if text2 is not None:
                    element = wait.until(EC.text_to_be_present_in_element((By.ID, "body"), text2))
                print('Found it!')
            except:
                try:
                    WebDriverWait(self.driver, 1).until(EC.text_to_be_present_in_element((By.ID, "error_msg"), "CHARMM was terminated abnormally"))
                    print('ERROR MESSAGE - check "screenshot_error.png"')
                    self.driver.save_screenshot("screenshot_error.png")
                    self.driver.quit()
                except:
                    self.wait_text(text, start_time=start_time)
        except:
            print('window has been closed')
            self.driver.quit()

    def model_select(self, option=None):
        """
        Selects non-protein chains in the model selections section.

        Parameters:
            option (int): Number of "unselected" chains (optional).
        """
        if option is None:
            pass
        else:
            check = False
            i = 4
            while not check:
                if option == 0:
                    break
                if self.driver.find_element(By.XPATH, f'/html/body/div[4]/div[2]/div[3]/div[2]/form/div/table/tbody/tr[{i}]/td[1]/input').is_selected():
                    i += 1
                else:
                    self.driver.find_element(By.XPATH, f'/html/body/div[4]/div[2]/div[3]/div[2]/form/div/table/tbody/tr[{i}]/td[1]/input').click()
                    option -= 1

    def preserve(self, option=None):
        """
        Checks the preserve hydrogen option.

        Parameters:
            option (any): Option to enable preserve hydrogen (optional).
        """
        if option is None:
            pass
        else:
            self.driver.find_element(By.ID, 'hbuild_checked').click()

    def read_het(self, het='UNK', source='sdf', gen_with='cgenff', lig_filename='UNK', ph_ligand=True, path=None, pH=None):
        """
        Selects parameters for non-protein chains/molecules.

        Parameters:
            het (str): Type of non-protein molecule ('CO3' for IONIZED CARBONATE, ADM JR., AUG 2001 or 'CO31' for HO3, BICARBONATE, XXWY & KEVO).
            source (str): Type of input files provided (mol2, sdf)
            gen_with (str): Type of programme used to generate the ligand parameters ('cgenff', 'antechamber', 'openff', 'charmm', 'CSML')
            lig_filename (str): File name of your source file. Assumes that path is the same as for the input PDB.

            WARNING: if gen_with == 'charmm' it is assumed that the .top and .par have the same filename
        """
        if het is None:
            het = 'UNK'
        print('reading het')
        if gen_with == 'CSML':
            self.driver.find_element(By.XPATH, f'//input[@name="rename[{het}]" and @value="rename"]').click()
            main_window = self.driver.window_handles[0]
            self.driver.find_element(By.XPATH, f'//input[@type="button" and @onclick="openCSMLSearch(\'{het}\')"]').click()
            popup = self.driver.window_handles[-1]
            self.driver.switch_to.window(popup)
            time.sleep(8)
            self.driver.find_element(By.XPATH, f"//input[@value='{het}']").click()
            self.nxt()
            self.driver.switch_to.window(main_window)
        elif gen_with == 'charmm':
            self.driver.find_element(By.XPATH, f"//input[@value='{gen_with}']").click()
            choose_file = self.driver.find_element(By.NAME, f'top[{het}]')
            file_location = os.path.join(path, lig_filename+'.top')
            choose_file.send_keys(file_location)
            choose_file = self.driver.find_element(By.NAME, f'par[{het}]')
            file_location = os.path.join(path, lig_filename+'.par')
            choose_file.send_keys(file_location)
        else:
            self.driver.find_element(By.XPATH, f"//input[@value='{gen_with}']").click()
            self.driver.find_element(By.XPATH, f"//input[@name='rename_option[{gen_with}][{het}]' and @value='{source}']").click()
            choose_file = self.driver.find_element(By.NAME, f'{source}_{gen_with}[{het}]')
            file_location = os.path.join(path, lig_filename+'.'+source)
            choose_file.send_keys(file_location)
            # self.driver.find_element(By.XPATH, f"//input[@id='ph_ligand]").click()
        if ph_ligand and not pH:
            print(f'If system pH is not set then ph_ligand will be equal to False!!! ({het})')
        element = self.driver.find_element(By.XPATH, f"//input[@id='ph_ligand' and @name='ph_ligand[{het}]']")
        sel = element.is_selected()
        #print(het, sel, ph_ligand)
        if sel is not ph_ligand:
            #print('in if')
            element.click()
            #self.driver.find_element(By.XPATH, f"//input[@id='ph_ligand' and @name='ph_ligand[{het}]']").click()








    def add_mutation(self, chain, rid, aa):
        """
        Enters mutations of residues.

        Parameters:
            chain (str): Chain identifier.
            rid (str): Residue ID.
            aa (str): Amino acid mutation.
        """
        if chain is None:
            pass
        else:
            if not self.driver.find_element(By.ID, 'id_mutation').is_displayed():
                self.driver.find_element(By.ID, 'mutation_checked').click()
                self.driver.find_element(By.XPATH, '//*[@id="id_mutation_table"]/tr[2]/td[5]/input').click()
            self.driver.find_element(By.XPATH, '//input[@value="Add Mutation"]').click()
            resids = [i.get_attribute('id') for i in self.driver.find_elements(By.XPATH, '//select[starts-with(@id,"mutation_chain_")]') if i.is_displayed()]
            resid = resids[-1][-1]
            Select(self.driver.find_element(By.ID, f'mutation_chain_{resid}')).select_by_value(chain)
            Select(self.driver.find_element(By.ID, f'mutation_rid_{resid}')).select_by_value(rid)
            Select(self.driver.find_element(By.ID, f'mutation_patch_{resid}')).select_by_value(aa)

    def system_pH(self, pH):
        """
        Sets or turns off the system pH settings.

        Parameters:
            pH (float): The desired pH value (optional).
        """
        if pH is None:
            self.driver.find_element(By.ID, 'ph_checked').click()
        else:
            t = self.driver.find_element(By.ID, 'system_pH')
            t.clear()
            t.send_keys(pH)
            self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div[3]/form/div[1]/input[3]').click()

    def add_protonation(self, chain, res_i, rid, res_p):
        """
        Adds side-chain protonations.

        Parameters:
            chain (str): Chain identifier.
            res_i (str): Initial residue.
            rid (str): Residue ID.
            res_p (str): Protonation type. (The value should be the same as in the Dropdown menu under 'Patch')
        """
        if chain is None:
            return
        else:
            if not self.driver.find_element(By.ID, 'id_prot').is_displayed():
                self.driver.find_element(By.ID, 'prot_checked').click()
            self.driver.find_element(By.XPATH, '//input[@value="Add Protonation"]').click()
            resids = [i.get_attribute('id') for i in self.driver.find_elements(By.XPATH, '//select[starts-with(@id,"prot_chain_")]') if i.is_displayed()]
            resid = resids[-1][-1]
            Select(self.driver.find_element(By.ID, f'prot_chain_{resid}')).select_by_value(chain)
            Select(self.driver.find_element(By.ID, f'prot_res_{resid}')).select_by_value(res_i)
            Select(self.driver.find_element(By.ID, f'prot_rid_{resid}')).select_by_value(rid)
            Select(self.driver.find_element(By.ID, f'prot_patch_{resid}')).select_by_value(res_p)

    def add_disulfide(self, chain1, rid1, chain2, rid2):
        """
        Adds disulfide bonds.

        Parameters:
            chain1 (str): First chain identifier.
            rid1 (str): First residue ID.
            chain2 (str): Second chain identifier.
            rid2 (str): Second residue ID.
        """
        if chain1 is None:
            pass
        else:
            if not self.driver.find_element(By.ID, 'id_dif').is_displayed():
                self.driver.find_element(By.ID, 'ssbonds_checked').click()
                while len([i.get_attribute('id') for i in self.driver.find_elements(By.XPATH, '//select[starts-with(@id,"ssbond_chain1")]') if i.is_displayed()]) != 0:
                    self.driver.find_element(By.XPATH, '//*[@id="id_dif_table"]/tr[2]/td[6]/input').click()
            self.driver.find_element(By.XPATH, '//input[@value="Add Bonds"]').click()
            resids = [i.get_attribute('id') for i in self.driver.find_elements(By.XPATH, '//select[starts-with(@id,"ssbond_chain1_")]') if i.is_displayed()]
            resid = resids[-1][-1]
            Select(self.driver.find_element(By.ID, f'ssbond_chain1_{resid}')).select_by_value(chain1)
            Select(self.driver.find_element(By.ID, f'ssbond_resid1_{resid}')).select_by_value(rid1)
            Select(self.driver.find_element(By.ID, f'ssbond_chain2_{resid}')).select_by_value(chain2)
            Select(self.driver.find_element(By.ID, f'ssbond_resid2_{resid}')).select_by_value(rid2)

    def add_phosphorylation(self, chain, res_i, rid, res_p):
        """
        Adds phosphorylations to residues.

        Parameters:
            chain (str): Chain identifier.
            res_i (str): Initial residue.
            rid (str): Residue ID.
            res_p (str): Phosphorylation type. (The value should be the same as in the Dropdown menu under 'Patch' ie. for TYR: [TP1, TP2], SER: [SP1, SP2], THR: [THP1, THPB], ARG: [RP1, RP2])
        """
        if chain is None:
            pass
        else:
            if not self.driver.find_element(By.ID, 'id_phos').is_displayed():
                self.driver.find_element(By.ID, 'phos_checked').click()
                self.driver.find_element(By.XPATH, '//*[@id="id_phos_table"]/tr[2]/td[5]/input').click()
            self.driver.find_element(By.XPATH, '//input[@value="Add Phosphorylation"]').click()
            resids = [i.get_attribute('id') for i in self.driver.find_elements(By.XPATH, '//select[starts-with(@id,"phos_chain_")]') if i.is_displayed()]
            resid = resids[-1][-1]
            Select(self.driver.find_element(By.ID, f'phos_chain_{resid}')).select_by_value(chain)
            Select(self.driver.find_element(By.ID, f'phos_res_{resid}')).select_by_value(res_i)
            Select(self.driver.find_element(By.ID, f'phos_rid_{resid}')).select_by_value(rid)
            Select(self.driver.find_element(By.ID, f'phos_patch_{resid}')).select_by_value(res_p)

    def sugar_options(self, sugar_id=1, link=None, ltype='B', sname='GLC'):
        """
        Parses sugar options.

        Parameters:
            sugar_id (int): Sugar identifier (default is 1).
            link (str): Link type (optional).
            ltype (str): Linkage type (default is 'B').
            sname (str): Sugar name (default is 'GLC').
        """
        Select(self.driver.find_element(By.ID, f'seq_name_{sugar_id}')).select_by_value(sname)
        Select(self.driver.find_element(By.ID, f'seq_type_{sugar_id}')).select_by_value(ltype)
        if link is not None:
            Select(self.driver.find_element(By.ID, f'seq_link_{sugar_id}')).select_by_value(str(link))

    def add_sugar(self, sid='1'):
        """
        Adds sugars to the system.

        Parameters:
            sid (str): Sugar identifier (default is '1').
        """
        self.driver.find_element(By.ID, sid).find_element(By.CLASS_NAME, 'add').click()

    def add_modification(self, sname=None, sugar_id=None, mod=None):
        """
        Adds chemical modifications.

        Parameters:
            sname (str): Sugar name (optional).
            sugar_id (int): Sugar identifier (optional).
            mod (str): Modification type (optional).
        """
        if mod is None:
            return
        if not self.driver.find_element(By.XPATH, '//input[@value="Add chemical modification"]').is_displayed():
            self.driver.find_element(By.ID, 'chem_checked').click()
        else:
            self.driver.find_element(By.XPATH, '//input[@value="Add chemical modification"]').click()
        resids = [i.get_attribute('id') for i in self.driver.find_elements(By.XPATH, '//select[starts-with(@id,"chem_res_")]') if i.is_displayed()]
        if len(resids) == 0:
            resids = [i.get_attribute('id') for i in self.driver.find_elements(By.XPATH, '//select[starts-with(@id,"chem_resid_")]') if i.is_displayed()]
        resid = resids[-1][-1]
        try:
            if self.driver.find_element(By.ID, f'chem_res_{resid}').is_displayed():
                Select(self.driver.find_element(By.ID, f'chem_res_{resid}')).select_by_value(sname)
        except:
            pass
        Select(self.driver.find_element(By.ID, f'chem_resid_{resid}')).select_by_value(str(sugar_id))
        Select(self.driver.find_element(By.ID, f'chem_site_{resid}')).select_by_value(mod[0])
        Select(self.driver.find_element(By.ID, f'chem_patch_{resid}')).select_by_value(mod[1:])

    def GRS_reader(self, GRS=None, skip=1):
        """
        Reads GRS input for glycans.

        Parameters:
            GRS (str): GRS input string (optional).
            skip (int): Number of lines to skip (default is 1).
        """
        if GRS is None:
            pass
        else:
            lipids_dict = {'CER': 'CER', 'PIC': 'PICER', 'DAG': 'DAG', 'PID': 'PIDAG', 'ACYL':'ACYL'}
            sugars_dict = {}
            branch_length = [(1,1)]
            # Making the sugar dictionary
            for i in GRS.split('\n'):
                sug = i.split(' ')
                if len(sug) > 2:
                    if '_' in sug[-1]:
                        sug = sug[:-1] + sug[-1].split('_')
                    else:
                        sug += [None]
                    sugars_dict[int(sug[0])] = {'sname': sug[-2][1:], 'sugar_id': int(sug[0])-1, 'ltype': sug[-2][0], 'mod': sug[-1]}
                    if sugars_dict[int(sug[0])]['sugar_id'] != 1:
                        sugars_dict[int(sug[0])]['link'] =  sug[-3][1]
                        if len(sug) > 1:
                            for j in branch_length[::-1]:
                                if len(sug)-3 > j[1]:
                                    branch_length.append((int(sug[0])-1, len(sug)-3))
                                    sugars_dict[int(sug[0])]['branch'] = j[0]
                                    break
                if len(sug) == 2:
                    if sug[-1][:3] != 'PRO':
                        sugars_dict[int(sug[0])] = {'lipid_type': lipids_dict[sug[-1].replace('-','')[:3]],'lipid_tail': sug[-1]}
                    else:
                        sugars_dict[int(sug[0])] = {'chain': sug[-1][:4], 'residue': sug[-1][-4:-1], 'resid': sug[-1][-1]}

            # Adding the sugars
            for i in range(skip, 1 + len(sugars_dict)):
                if i == 1:
                    if sugars_dict[i].get('lipid_type') is not None:
                        Select(self.driver.find_element(By.ID, 'lipid_types')).select_by_value(sugars_dict[i]['lipid_type'])
                        Select(self.driver.find_element(By.ID, 'seq_name_0')).select_by_value(sugars_dict[i]['lipid_tail'])
                    else:
                        Select(self.driver.find_element(By.ID, 'seq_name_0')).select_by_value(sugars_dict[i]['chain'])
                        Select(self.driver.find_element(By.ID, 'seq_name2_0')).select_by_value(sugars_dict[i]['residue'])
                        Select(self.driver.find_element(By.ID, 'seq_name3_0')).select_by_value(sugars_dict[i]['resid'])
                elif i == 2:
                    self.sugar_options(sugar_id=sugars_dict[i]['sugar_id'], link=sugars_dict[i].get('link', None), ltype=sugars_dict[i]['ltype'], sname=sugars_dict[i]['sname'])
                    self.add_modification(sname=sugars_dict[i]['sname'], sugar_id=sugars_dict[i]['sugar_id'], mod=sugars_dict[i]['mod'])
                else:
                    self.add_sugar(sugars_dict[i]['branch'])
                    self.sugar_options(sugar_id=sugars_dict[i]['sugar_id'], link=sugars_dict[i].get('link', None), ltype=sugars_dict[i]['ltype'], sname=sugars_dict[i]['sname'])
                    self.add_modification(sname=sugars_dict[i]['sname'], sugar_id=sugars_dict[i]['sugar_id'], mod=sugars_dict[i]['mod'])

    def add_gpi(self, GRS=None, chain=None, skip=6):
        """
        Adds GPI anchors.

        Parameters:
            GRS (str): GRS input string (optional).
            chain (str): Chain identifier (optional).
            skip (int): Number of lines to skip (default is 6).
        """
        if GRS is None:
            pass
        else:
            self.driver.find_element(By.ID, 'gpi_checked').click()
            Select(self.driver.find_element(By.ID, 'gpi_chain')).select_by_value(f'{chain}')
            main_window = self.driver.window_handles[0]
            self.driver.find_element(By.XPATH, '//*[@id="gpi"]/td[4]/input').click()
            popup = self.driver.window_handles[-1]
            self.driver.switch_to.window(popup)
            time.sleep(2)
            self.GRS_reader(GRS, skip=skip)
            self.nxt()
            self.driver.switch_to.window(main_window)

    def add_glycan(self, GRS, skip=1):
        """
        Adds glycans.

        Parameters:
            GRS (str): GRS input string.
            skip (int): Number of lines to skip (default is 1).
        """
        if GRS is None:
            pass
        else:
            if not self.driver.find_element(By.ID, 'add_glycosylation').is_displayed():
                self.driver.find_element(By.ID, 'glyc_checked').click()
            self.driver.find_element(By.ID, 'add_glycosylation').click()
            main_window = self.driver.window_handles[0]
            glyc_id = self.driver.find_elements(By.XPATH, '//*[starts-with(@id, "glycan_CAR")]')[-1].get_attribute('id')
            self.driver.find_element(By.XPATH, f'//*[@id="{glyc_id}"]/td[5]/input').click()

            popup = self.driver.window_handles[-1]
            self.driver.switch_to.window(popup)
            time.sleep(2)
            self.GRS_reader(GRS, skip=skip)
            self.nxt()
            self.driver.switch_to.window(main_window)

    def patch(self, chain=None, ter=None, ter_patch=None):
        """
        Adds terminal patches.

        Parameters:
            chain (str): Chain identifier (optional).
            ter (str): Terminal type (optional).
            ter_patch (str): Terminal patch type (optional).
        """
        if chain is None:
            pass
        else:
            Select(self.driver.find_element(By.NAME, f'terminal[{chain}][{ter}]')).select_by_value(f'{ter_patch}')

    def waterbox(self, size='implicit', shape='rect', dis=10.0, X=10.0, Y=10.0, Z=10.0):
        """
        Configures the water box.

        Parameters:
            size (str): Size type ('explicit' or 'implicit').
            shape (str): Shape type ('rect' or 'octa').
            dis (float): Distance for implicit size (default is 10.0).
            X (float): X dimension for explicit size (default is 10.0).
            Y (float): Y dimension for explicit size (default is 10.0).
            Z (float): Z dimension for explicit size (default is 10.0).
        """
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
        """
        Sets the ion method.

        Parameters:
            method (str): Ion method ('mc' or 'dist', optional).
        """
        if method is None:
            return
        Select(self.driver.find_element(By.NAME, 'ion_method')).select_by_value(method)

    def clear_ion(self):
        """
        Clears ions from the configuration.
        """
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.XPATH, '//*[@id="ions_table"]/tbody/tr/td[6]/input').click()

    def add_ion(self, formula, conc=0.15, neu=True):
        """
        Adds ions to the system.

        Parameters:
            formula (str): Ion formula ('KCl', 'NaCl', 'CaCl2', or 'MgCl2').
            conc (float): Ion concentration (default is 0.15).
            neu (bool): Whether the ions are neutral (default is True).
        """
        Select(self.driver.find_element(By.ID, 'ion_type')).select_by_value(formula)
        self.driver.find_element(By.XPATH, '//*[@id="simple_ions_widget"]/input').click()
        if conc != 0.15:
            c = self.driver.find_element(By.XPATH, '//*[@id="ions_table"]/tbody/tr[1]/td[4]/input')
            c.clear()
            c.send_keys(conc)
        if not neu:
            self.driver.find_element(By.XPATH, '//*[@id="ions_table"]/tbody/tr[1]/td[5]/input').click()

    def calc_solv(self):
        """
        Calculates the solvation of the system.
        """
        self.driver.find_element(By.XPATH, '//*[@id="fsolution"]/div[6]/input').click()

    def sys_type(self, systype):
        """
        Sets the system type.

        Parameters:
            systype (str): System type ('solution', 'bilayer', 'micelle', or 'nanodisc').
        """
        Select(self.driver.find_element(By.NAME, 'systype')).select_by_value(systype.lower())

    def force_field(self, ff, amber_options = None):
        """
        Sets the force field type.

        Parameters:
            ff (str): Force field type ('c36m', 'c36', 'amber', or 'opls').
            amber_options: Which AMBER FF options to use ['amberff_prot': ,'amberff_dna','amberff_rna','amberff_glycan', 'amberff_lipid','amberff_water','amberff_ligand']
        """
        Select(self.driver.find_element(By.NAME, 'fftype')).select_by_value(ff)
        if ff == 'amber':
            amber_options_default = {'Protein': 'FF19SB','DNA': 'OL15','RNA': 'OL3','Glycan': 'GLYCAM_06j', 'Lipid': 'Lipid21','Water': 'OPC','Ligand': 'GAFF2'}
            if amber_options is not None:
                 for key, value in amber_options.items():
                    amber_options_default[key.capitalize()] = value
            Select(self.driver.find_element(By.ID, 'amberff_prot')).select_by_value(amber_options_default['Protein'])
            Select(self.driver.find_element(By.ID, 'amberff_dna')).select_by_value(amber_options_default['DNA'])
            Select(self.driver.find_element(By.ID, 'amberff_rna')).select_by_value(amber_options_default['RNA'])
            Select(self.driver.find_element(By.ID, 'amberff_glycan')).select_by_value(amber_options_default['Glycan'])
            Select(self.driver.find_element(By.ID, 'amberff_lipid')).select_by_value(amber_options_default['Lipid'])
            Select(self.driver.find_element(By.ID, 'amberff_water')).select_by_value(amber_options_default['Water'])
            Select(self.driver.find_element(By.ID, 'amberff_ligand')).select_by_value(amber_options_default['Ligand'])

    def engine(self, software):
        """
        Sets the simulation engine.

        Parameters:
            software (str): Simulation software ('namd', 'gmx', 'amb', 'omm', 'comm', 'gns', 'dms', 'lammps', or 'tinker').
        """
        self.driver.find_element(By.XPATH, f'//*[@id="input_{software}"]/td/input').click()

    def temperature(self, temp=303.15):
        """
        Sets the temperature for the simulation..

        Parameters:
            temp (float): Temperature in Kelvin (default is 303.15).
        """
        if temp != 303.15:
            t = self.driver.find_element(By.NAME, 'temperature')
            t.clear()
            t.send_keys(temp)

    def download(self, jobid):
        """
        Downloads and unpacks the simulation files.

        Parameters:
            jobid (str): Job ID for which to download the files.
        """
        os.system(f'mkdir {out_tmp}')
        print('starting download')
        try:
            self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div[2]/div[8]/a').click()
        except:
            try:
                self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div[2]/div[6]/a').click()
            except:
                self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div[2]/div[3]/a').click()
        while not os.path.isfile(f'{out_tmp}/charmm-gui.tgz'):
            time.sleep(10)
        print('Download done - unpacking starting')
        time.sleep(10)
        unpacked = True
        while unpacked:
            try:
                subprocess.run(['tar', '-xf', f'{out_tmp}/charmm-gui.tgz', '-C', f'{self.path_out}/'], check=True)
                unpacked = False
                break
            except subprocess.CalledProcessError as e:
                time.sleep(5)
        os.system(f'rm -r {out_tmp}')
        print('Unpacked')

    def manipulate_PDB(self, path=None, file_name=None, pdb_id=None, model=None, chains=None, hets=None, pH=None, preserve={'option': None}, mutations=None, protonations=None, disulfides=None, phosphorylations=None, gpi={'GRS': None}, glycans=None):
        """
        Manipulates a PDB file with various options.

        Parameters:
            path (str): Directory path where the PDB file is located (optional).
            file_name (str): Name of the PDB file (optional).
            pdb_id (str): PDB ID for fetching the file (optional).
            model (any): Model selection options (optional).
            chains (list): List of chains to be patched (optional).
            het (str): Type of non-protein molecule (optional).
            pH (float): Desired pH value (optional).
            preserve (dict): Preserve hydrogen options (default is {'option': None}).
            mutations (list): List of mutations to add (optional).
            protonations (list): List of protonations to add (optional).
            disulfides (list): List of disulfide bonds to add (optional).
            phosphorylations (list): List of phosphorylations to add (optional).
            gpi (dict): GPI anchor options (default is {'GRS': None}).
            glycans (list): List of glycans to add (optional).

        Returns:
            jobid (str): Job ID for the manipulated PDB file.
        """
        # if file_name is not None:
        #     self.upload(file_name, path)
        # else:
        #     self.from_pdb(pdb_id)

        self.wait_text("Model/Chain Selection Option")
        jobid = self.driver.find_element(By.CLASS_NAME, "jobid").text
        print(jobid)
        self.model_select(model)
        self.nxt()
        self.wait_text("PDB Manipulation Options")
        self.system_pH(pH)
        if chains is not None:
            for chain in chains:
                self.patch(chain[0], chain[1], chain[2])
        if hets is not None:
            for het in hets:
                self.read_het(**het, path=path, pH=pH)
                #self.read_het(het, source, gen_with, lig_filename, ph_ligand, path)
        self.preserve(**preserve)
        if mutations is not None:
            for mutation in mutations:
                self.add_mutation(**mutation)
        if protonations is not None:
            for protonation in protonations:
                self.add_protonation(**protonation)
        if disulfides is not None:
            ### Removes disulfides automatically added by CharmmGUI
            if self.driver.find_element(By.ID, 'id_dif').is_displayed():
                ### Creates the disulfides display as a variable so that the remove elements are only looked for within it (to avoid removing protonations, mutations, etc.)
                disulfides_display = self.driver.find_element(By.ID, 'id_dif')
                while disulfides_display.find_elements(By.XPATH, './/input[@value="-"]'): ### Returns empty list if no more disulfide bonds
                    disulfides_display.find_element(By.XPATH, './/input[@value="-"]').click() ### Clicks remove button for first disulfide bond
            for disulfide in disulfides:
                self.add_disulfide(**disulfide)
        if phosphorylations is not None:
            for phosphorylation in phosphorylations:
                self.add_phosphorylation(**phosphorylation)
        self.add_gpi(**gpi, skip=6)
        if glycans is not None:
            for glycan in glycans:
                self.add_glycan(**glycan, skip=1)
        return jobid
        time.sleep(1000)

class Retrieve(CharmmGuiAuto):
    def run(self, email, password, jobid):
        """
        Runs the retrieval process to download files for a given job ID.

        Parameters:
            email (str): User's email address.
            password (str): User's password.
            jobid (str): Job ID to retrieve.
        """
        try:
            self.login(email, password)
            time.sleep(2)
            self.wait_text('enter your Job ID')
            self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/form/input[1]').send_keys(jobid)
            self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/form/input[2]').click()
            self.wait_text("Job found")
            if 'membrane.bilayer' in self.driver.page_source:
                self.driver.get(f'https://www.charmm-gui.org/?doc=input/membrane.bilayer&step=6&project=membrane_bilayer&jobid={jobid}')
                self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div[2]/div[8]/a').click()
            else:
                self.driver.get(f'https://www.charmm-gui.org/?doc=input/solution&step=4&project=solution&jobid={jobid}')
                self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div[2]/div[6]/a').click()

            while not os.path.isfile(f'{out_tmp}/charmm-gui.tgz'):
                time.sleep(10)

            print('Download done - unpacking starting')
            time.sleep(10)
            unpacked = True
            while unpacked:
                try:
                    subprocess.run(['tar', '-xf', f'{out_tmp}/charmm-gui.tgz', '-C', f'{self.path_out}/'], check=True)
                    unpacked = False
                    break
                except subprocess.CalledProcessError as e:
                    time.sleep(5)
            os.system(f'rm -r {out_tmp}')
            print('Unpacked')
            self.driver.quit()
            print(f'Job done - output under \"{self.path_out}/charmm-gui-{jobid}\"')
        except:
            print('Exception raised')
            self.driver.quit()
            raise ValueError('A very specific bad thing happened.')

class PDBReader(CharmmGuiAuto):
    def run(self, email, password, path=None, screenshot=False, file_name=None, download_now=True, pdb_id=None, model=None, chains=None, hets=None, pH=None, preserve={'option': None}, mutations=None, protonations=None, disulfides=None, phosphorylations=None, gpi={'GRS': None}, glycans=None):
        """
        Runs the PDB Reader and manipulates a PDB file.

        Parameters:
            email (str): User's email address.
            password (str): User's password.
            path (str): Directory path where the PDB file is located (optional).
            file_name (str): Name of the PDB file (optional).
            download_now (bool): Whether to download the output immediately (default is True).
            pdb_id (str): PDB ID for fetching the file (optional).
            model (any): Model selection options (optional).
            chains (list): List of chains to be patched (optional).
            het (str): Type of non-protein molecule (optional).
            pH (float): Desired pH value (optional).
            preserve (dict): Preserve hydrogen options (default is {'option': None}).
            mutations (list): List of mutations to add (optional).
            protonations (list): List of protonations to add (optional).
            disulfides (list): List of disulfide bonds to add (optional).
            phosphorylations (list): List of phosphorylations to add (optional).
            gpi (dict): GPI anchor options (default is {'GRS': None}).
            glycans (list): List of glycans to add (optional).
        """
        try:
            self.login(email, password)
            self.wait_text('PDB Reader & Manipulator')
            time.sleep(5)
            if file_name is not None:
                self.upload(file_name, path)
            else:
                self.from_pdb(pdb_id)
            time.sleep(1)
            jobid = self.manipulate_PDB(path, file_name, pdb_id, model, chains, hets, pH, preserve, mutations, protonations, disulfides, phosphorylations, gpi, glycans)
            self.nxt(prev_step="PDB Manipulation", screen=screenshot, jobid=jobid)
            self.wait_text('Computed Energy')
            if download_now:
                print(f'Ready to download from retrieve job id {jobid}')
                self.download(jobid)
                self.driver.quit()
                print(f'Job done - output under \"{self.path_out}charmm-gui-{jobid.split(" ")[-1]}\"')
            else:
                self.driver.quit()
                print(f'Job done, but has not been retrieved JOBID: {jobid.split(" ")[-1]}')
        except:
            print('Exception raised')
            self.driver.quit()
            raise ValueError('A very specific bad thing happened.')

class FFConverter(CharmmGuiAuto):
    def run(self, email, password, path=None, screenshot=False, file_name=None, download_now=True, PBC=False, PBC_x=10, systype='Solution', ff='c36m', amber_options=None, engine='gmx', temp=310):
        """
        Runs the Force Field Converter.

        Parameters:
            email (str): User's email address.
            password (str): User's password.
            path (str): Directory path where the PSF file is located (optional).
            file_name (str): Name of the PSF file (optional).
            download_now (bool): Whether to download the output immediately (default is True).
            PBC (bool): Whether to set up periodic boundary conditions (default is False).
            PBC_x (float): Size of the PBC box (default is 10).
            systype (str): System type ('Solution', 'Bilayer', etc., default is 'Solution').
            ff (str): Force field type (default is 'c36m').
            amber_options (dict): AMBER FF options (default is None).
            engine (str): Simulation engine (default is 'gmx').
            temp (float): Temperature in Kelvin (default is 310).
        """
        try:
            self.login(email, password)
            self.wait_text('Force Field Converter')
            time.sleep(1)
            # Upload PSF File
            choose_file = self.driver.find_element(By.ID, 'psffile')
            file_location = os.path.join(path, 'step1_pdbreader.psf')
            choose_file.send_keys(file_location)
            # Upload CRD File
            choose_file = self.driver.find_element(By.ID, 'crdfile')
            file_location = os.path.join(path, 'step1_pdbreader.crd')
            choose_file.send_keys(file_location)
            # Upload additional files
            self.driver.find_element(By.NAME, "add_toppar").click()
            choose_file = self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/span[2]/div[1]/form/p[2]/table/tbody/tr/td[4]/input')
            file_location = os.path.join(path, 'step1_pdbreader.str')
            choose_file.send_keys(file_location)
            if PBC:
                t = self.driver.find_element(By.NAME, 'box[cube][x]')
                t.clear()
                t.send_keys(PBC_x)
            else:
                self.driver.find_element(By.ID, 'setup_pbc').click()
            self.nxt()
            self.wait_text('System Information')
            jobid = self.driver.find_element(By.CLASS_NAME, "jobid").text
            print(jobid)
            self.sys_type(systype)
            self.force_field(ff, amber_options)
            self.engine(engine)
            self.temperature(temp)
            self.nxt(prev_step="System Information", screen=screenshot, jobid=jobid)
            self.wait_text("to continue equilibration and production simulations")
            if download_now:
                print(f'Ready to download from retrieve job id {jobid}')
                self.download(jobid)
                self.driver.quit()
                print(f'Job done - output under \"{self.path_out}charmm-gui-{jobid.split(" ")[-1]}\"')
            else:
                self.driver.quit()
                print(f'Job done, but has not been retrieved JOBID: {jobid.split(" ")[-1]}')
        except:
            print('Exception raised')
            self.driver.quit()
            raise ValueError('A very specific bad thing happened.')

class PDBReaderFFConverter(CharmmGuiAuto):
    def run(self, email, password, path=None, screenshot=False, file_name=None, download_now=True, pdb_id=None, model=None, hets=None, chains=None, het=None, pH=None, preserve={'option': None}, mutations=None, protonations=None, disulfides=None, phosphorylations=None, gpi={'GRS': None}, glycans=None, PBC=False, PBC_x=10, systype='Solution', ff='c36m', amber_options = None, engine='gmx', temp=310):
        """
        Runs both the PDB Reader and Force Field Converter.

        Parameters:
            email (str): User's email address.
            password (str): User's password.
            path (str): Directory path where the PDB file is located (optional).
            file_name (str): Name of the PDB file (optional).
            download_now (bool): Whether to download the output immediately (default is True).
            pdb_id (str): PDB ID for fetching the file (optional).
            model (any): Model selection options (optional).
            chains (list): List of chains to be patched (optional).
            het (str): Type of non-protein molecule (optional).
            pH (float): Desired pH value (optional).
            preserve (dict): Preserve hydrogen options (default is {'option': None}).
            mutations (list): List of mutations to add (optional).
            protonations (list): List of protonations to add (optional).
            disulfides (list): List of disulfide bonds to add (optional).
            phosphorylations (list): List of phosphorylations to add (optional).
            gpi (dict): GPI anchor options (default is {'GRS': None}).
            glycans (list): List of glycans to add (optional).
            PBC (bool): Whether to set up periodic boundary conditions (default is False).
            PBC_x (float): Size of the PBC box (default is 10).
            systype (str): System type ('Solution', 'Bilayer', etc., default is 'Solution').
            ff (str): Force field type (default is 'c36m').
            amber_options (dict): AMBER FF options (default is None).
            engine (str): Simulation engine (default is 'gmx').
            temp (float): Temperature in Kelvin (default is 310).
        """
        try:
            self.login(email, password)
            self.wait_text('PDB Reader & Manipulator')
            time.sleep(1)
            if file_name is not None:
                self.upload(file_name, path)
            else:
                self.from_pdb(pdb_id)
            jobid1 = self.manipulate_PDB(path, file_name, pdb_id, model, chains, het, pH, preserve, mutations, protonations, disulfides, phosphorylations, gpi, glycans)
            self.nxt(prev_step="PDB Manipulation", screen=screenshot, jobid=jobid1)
            self.wait_text('Computed Energy')
            print(f'Ready to download from retrieve job id {jobid1}')
            self.download(jobid1)
            print(f'PDBReader done - output under \"{self.path_out}charmm-gui-{jobid1.split(" ")[-1]}\"')
            path_PDBReader = f'{self.path_out}charmm-gui-{jobid1.split(" ")[-1]}'
            #PDBReader done moving on to FFConverter
            self.driver.get('https://www.charmm-gui.org/?doc=input/converter.ffconverter')
            self.wait_text('Force Field Converter')
            time.sleep(1)
            # Upload PSF File
            choose_file = self.driver.find_element(By.ID, 'psffile')
            file_location = os.path.join(path_PDBReader, 'step1_pdbreader.psf')
            choose_file.send_keys(file_location)
            # Upload CRD File
            choose_file = self.driver.find_element(By.ID, 'crdfile')
            file_location = os.path.join(path_PDBReader, 'step1_pdbreader.crd')
            choose_file.send_keys(file_location)
            # Upload additional files
            self.driver.find_element(By.NAME, "add_toppar").click()
            choose_file = self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/span[2]/div[1]/form/p[2]/table/tbody/tr/td[4]/input')
            file_location = os.path.join(path_PDBReader, 'step1_pdbreader.str')
            choose_file.send_keys(file_location)
            if PBC:
                t = self.driver.find_element(By.NAME, 'box[cube][x]')
                t.clear()
                t.send_keys(PBC_x)
            else:
                self.driver.find_element(By.ID, 'setup_pbc').click()
            self.nxt()
            self.wait_text('System Information')
            jobid = self.driver.find_element(By.CLASS_NAME, "jobid").text
            print(jobid)
            self.sys_type(systype)
            self.force_field(ff, amber_options)
            self.engine(engine)
            self.temperature(temp)
            self.nxt(prev_step="PDB Manipulation", screen=screenshot, jobid=jobid)
            self.wait_text("to continue equilibration and production simulations")
            if download_now:
                print(f'Ready to download from retrieve job id {jobid}')
                self.download(jobid)
                self.driver.quit()
                print(f'Job done - output under \"{self.path_out}charmm-gui-{jobid.split(" ")[-1]}\"')
            else:
                self.driver.quit()
                print(f'Job done, but has not been retrieved JOBID: {jobid.split(" ")[-1]}')
        except:
            print('Exception raised')
            self.driver.quit()
            raise ValueError('A very specific bad thing happened.')

class SolutionProtein(CharmmGuiAuto):
    def run(self, email, password, path=None, file_name=None, screenshot=False, download_now=True, pdb_id=None, model=None, chains=None, hets=None, pH=None, preserve={'option': None}, mutations=None, protonations=None, disulfides=None, phosphorylations=None, gpi={'GRS': None}, glycans=None, ions='NaCl', ff='c36m', amber_options = None, engine='gmx', temp='310', waterbox={'dis': 10.0}, ion_method=None):
        """
        Runs the Solution Protein setup and simulation.

        Parameters:
            email (str): User's email address.
            password (str): User's password.
            path (str): Directory path where the PDB file is located (optional).
            file_name (str): Name of the PDB file (optional).
            download_now (bool): Whether to download the output immediately (default is True).
            pdb_id (str): PDB ID for fetching the file (optional).
            model (any): Model selection options (optional).
            chains (list): List of chains to be patched (optional).
            het (str): Type of non-protein molecule (optional).
            pH (float): Desired pH value (optional).
            preserve (dict): Preserve hydrogen options (default is {'option': None}).
            mutations (list): List of mutations to add (optional).
            protonations (list): List of protonations to add (optional).
            disulfides (list): List of disulfide bonds to add (optional).
            phosphorylations (list): List of phosphorylations to add (optional).
            gpi (dict): GPI anchor options (default is {'GRS': None}).
            glycans (list): List of glycans to add (optional).
            ions (str): Ion type (default is 'NaCl').
            ff (str): Force field type (default is 'c36m').
            amber_options (dict): AMBER FF options (default is None).
            engine (str): Simulation engine (default is 'gmx').
            temp (float): Temperature in Kelvin (default is 310).
            waterbox (dict): Waterbox configuration (default is {'dis': 10.0}).
            ion_method (str): Ion method (optional).
        """
        try:
            self.login(email, password)
            self.wait_text("Protein Solution System")
            time.sleep(2)
            if file_name is not None:
                self.upload(file_name, path)
            else:
                self.from_pdb(pdb_id)
            self.wait_text("Model/Chain Selection Option")
            # jobid = self.driver.find_element(By.CLASS_NAME, "jobid").text
            # print(jobid)
            # self.model_select(model)
            # self.nxt()
            # self.wait_text("PDB Manipulation Options")
            jobid = self.manipulate_PDB(path, file_name, pdb_id, model, chains, hets, pH, preserve, mutations, protonations, disulfides, phosphorylations, gpi, glycans)

            # if chains is not None:
            #     for chain in chains:
            #         self.patch(chain[0], chain[1], chain[2])
            # if het is not None:
            #     self.read_het(het, source, gen_with, lig_filename, ph_ligand)
            # self.system_pH(pH)
            # self.preserve(**preserve)
            # if mutations is not None:
            #     for mutation in mutations:
            #         self.add_mutation(**mutation)
            # if protonations is not None:
            #     for protonation in protonations:
            #         self.add_protonation(**protonation)
            # if disulfides is not None:
            #     for disulfide in disulfides:
            #         self.add_disulfide(**disulfide)
            # if phosphorylations is not None:
            #     for phosphorylation in phosphorylations:
            #         self.add_phosphorylation(**phosphorylation)
            # self.add_gpi(**gpi, skip=6)
            # if glycans is not None:
            #     for glycan in glycans:
            #         self.add_glycan(**glycan, skip=1)
            self.nxt(prev_step="PDB Manipulation", screen=screenshot, jobid=jobid)
            self.wait_text("Add Ions")
            self.waterbox(**waterbox)
            self.ion_method(ion_method)
            self.clear_ion()
            self.add_ion(ions)
            self.calc_solv()
            self.nxt(prev_step="Add Ions", screen=screenshot, jobid=jobid)
            self.wait_text('Periodic Boundary Condition Options')
            self.nxt(prev_step="Periodic Boundary Condition Options", screen=screenshot, jobid=jobid)
            self.wait_text("Force Field Options")
            self.force_field(ff, amber_options)
            self.engine(engine)
            self.temperature(temp)
            self.nxt(prev_step="Force Field Options", screen=screenshot, jobid=jobid)
            self.wait_text("to continue equilibration and production simulations")
            if download_now:
                print(f'Ready to download from retrieve job id {jobid}')
                self.download(jobid)
                self.driver.quit()
                print(f'Job done - output under \"{self.path_out}charmm-gui-{jobid.split(" ")[-1]}\"')
            else:
                self.driver.quit()
                print(f'Job done, but has not been retrieved JOBID: {jobid.split(" ")[-1]}')
        except:
            print('Exception raised')
            self.driver.quit()
            raise ValueError('A very specific bad thing happened.')

class MembraneProtein(CharmmGuiAuto):
    """
    Membrane protein simulation setup.
    """

    def orientation(self, option='PDB', first_point=None, second_point=None, unchecked=None):
        """
        Sets the orientation of the membrane protein.

        Parameters:
            option (str): Orientation option ('PDB', 'Principal', 'Vector', 'PPM').
            first_point (list): First point for vector alignment (optional).
            second_point (list): Second point for vector alignment (optional).
            unchecked (list): List of chains not sent to PPM server (optional).
        """
        o = ['PDB', 'Principal', 'Vector', 'PPM'].index(option)
        self.driver.find_elements(By.NAME, 'align_option')[o].click()
        if o == 2:
            for j, point in enumerate([first_point, second_point]):
                self.driver.find_element(By.ID, f'align[{j}][segid]').clear()
                self.driver.find_element(By.ID, f'align[{j}][segid]').send_keys(point[0])
                self.driver.find_element(By.ID, f'align[{j}][residue]').clear()
                self.driver.find_element(By.ID, f'align[{j}][residue]').send_keys(point[1])
                self.driver.find_element(By.ID, f'align[{j}][resid]').clear()
                self.driver.find_element(By.ID, f'align[{j}][resid]').send_keys(point[2])
        if o == 3 and unchecked is not None:
            for j in unchecked:
                self.driver.find_element(By.NAME, f'ppm_chains[{j}]').click()

    def position(self, option=None, value=None):
        """
        Sets the position of the membrane protein.

        Parameters:
            option (str): Position option ('X', 'Y', 'Z', 'flip', optional).
            value (any): Value for the position option (optional).
        """
        print(option)
        if option is None:
            return
        options = {'X': 'rotate_x_checked', 'Y': 'rotate_y_checked', 'Z': 'translate_checked', 'flip': 'flip_checked'}
        self.driver.find_element(By.NAME, options[option]).click()
        if option != 'flip':
            values = {'X': 'rxdeg', 'Y': 'rydeg', 'Z': 'zdist'}
            self.driver.find_element(By.NAME, values[option]).clear()
            self.driver.find_element(By.NAME, values[option]).send_keys(value)

    def area(self, option=None, radius=None):
        """
        Sets the area of the membrane protein.

        Parameters:
            option (str): Area option (optional).
            radius (float): Radius for the area option (optional).
        """
        if option is None:
            return
        self.driver.find_element(By.NAME, 'fill_checked').click()
        if option != 'rot':
            self.driver.find_elements(By.NAME, 'filltype')[1].click()
            self.driver.find_element(By.NAME, 'crad').send_keys(radius)

    def projection(self, option=None):
        """
        Sets the projection of the membrane protein.

        Parameters:
            option (str): Projection option ('upper' or 'lower', optional).
        """
        if option is None:
            return
        self.driver.find_element(By.NAME, f'prot_projection_{option}').click()

    def box_type(self, option=None):
        """
        Sets the box type for the simulation.

        Parameters:
            option (str): Box type ('rect' or 'hexa', optional).
        """
        if option is None:
            return
        Select(self.driver.find_element(By.NAME, 'hetero_boxtype')).select_by_value(option)

    def lengthZ(self, option=None, value=None):
        """
        Sets the length in the Z direction.

        Parameters:
            option (str): Length option ('wdist' or 'nhydration', optional).
            value (float): Value for the length option (optional).
        """
        if option is None:
            return
        o = ['wdist', 'nhydration'].index(option)
        default = [(22.5, 'hetero_wdist'), (50, 'hetero_nhydration')]
        if value is None:
            value = default[o][0]
        self.driver.find_elements(By.NAME, 'hetero_z_option')[o].click()
        self.driver.find_element(By.NAME, default[o][1]).clear()
        self.driver.find_element(By.NAME, default[o][1]).send_keys(value)

    def lengthXY(self, option='ratio', value=20):
        """
        Sets the length in the XY direction.

        Parameters:
            option (str): Length option ('ratio' or 'nlipid', optional).
            value (float): Value for the length option (optional).
        """
        if option is None:
            return
        options = {'ratio': 'hetero_lx', 'nlipid': 'hetero_xvsy'}
        if option == 'nlipid':
            self.driver.find_elements(By.ID, 'hetero_xy_nlipid')[0].click()
        else:
            self.driver.find_element(By.XPATH, '//input[@name="hetero_lx" and @type="text"]').clear()
            self.driver.find_element(By.XPATH, '//input[@name="hetero_lx" and @type="text"]').send_keys(value)

    def add_lipid(self, lipid, upper, lower):
        """
        Adds lipids to the system.

        Parameters:
            lipid (str): Lipid type.
            upper (int): Number of lipids in the upper leaflet.
            lower (int): Number of lipids in the lower leaflet.
        """
        print(lipid)
        try:
            buttons = self.driver.find_elements(By.XPATH, "//img[contains(@src,'tri.png')]")
            if len(buttons) != 0:
                [x.click() for x in buttons if x.is_displayed()]
            u = self.driver.find_element(By.NAME, f'lipid_ratio[upper][{lipid}]')
            u.clear()
            u.send_keys(upper)
            l = self.driver.find_element(By.NAME, f'lipid_ratio[lower][{lipid}]')
            l.clear()
            l.send_keys(lower)
        except:
            try:
                buttons = self.driver.find_elements(By.XPATH, "//img[contains(@src,'tri.png')]")
                if len(buttons) != 0:
                    [x.click() for x in buttons if x.is_displayed()]
                u = self.driver.find_element(By.NAME, f'lipid_number[upper][{lipid}]')
                u.clear()
                u.send_keys(upper)
                l = self.driver.find_element(By.NAME, f'lipid_number[lower][{lipid}]')
                l.clear()
                l.send_keys(lower)
            except:
                print(lipid, upper, lower)

    def show_system_info(self):
        """
        Displays the system information.
        """
        try:
            element = self.driver.find_element(By.ID, 'hetero_size_button') # CSS_SELECTOR  #hetero_xy_option_nlipid > p:nth-child(4) > input:nth-child(1)
            self.driver.execute_script("arguments[0].scrollIntoView()", element)
            element.click()
        except:
            element = self.driver.find_element(By.CSS_SELECTOR, '#hetero_xy_option_nlipid > p:nth-child(4) > input:nth-child(1)') ##hetero_xy_option_ratio > p:nth-child(4) > input:nth-child(1)
            self.driver.execute_script("arguments[0].scrollIntoView()", element)
            element.click()
        time.sleep(1)

    def add_naa(self, lipid='LAU', aa='GLY', cter='CTER', lower=1, upper=1):
        """
        Adds N-acylated amino acids to the system.

        Parameters:
            lipid (str): Lipid type (default is 'LAU').
            aa (str): Amino acid type (default is 'GLY').
            cter (str): C-terminal type (default is 'CTER').
            lower (int): Number of lipids in the lower leaflet (default is 1).
            upper (int): Number of lipids in the upper leaflet (default is 1).
        """
        prevs = [i.get_attribute('value') for i in self.driver.find_elements(By.XPATH, '//input[starts-with(@value, "NAA")]')]
        if len(prevs) != 0:
            prev = sorted(set(prevs))[-1][-1]
            new = chr(ord(prev) + 1).upper()
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
        try:
            u = self.driver.find_element(By.NAME, f'lipid_ratio[upper][naa{new_l}]')
            u.clear()
            u.send_keys(upper)
            l = self.driver.find_element(By.NAME, f'lipid_ratio[lower][naa{new_l}]')
            l.clear()
            l.send_keys(lower)
        except:
            u = self.driver.find_element(By.NAME, f'lipid_number[upper][naa{new_l}]')
            u.clear()
            u.send_keys(upper)
            l = self.driver.find_element(By.NAME, f'lipid_number[lower][naa{new_l}]')
            l.clear()
            l.send_keys(lower)

    def add_peg(self, lipid='DAG', tail='DLGL', units=5, lower=1, upper=1):
        """
        Adds PEG lipids to the system.

        Parameters:
            lipid (str): Lipid type (default is 'DAG').
            tail (str): Tail type (default is 'DLGL').
            units (int): Number of units (default is 5).
            lower (int): Number of lipids in the lower leaflet (default is 1).
            upper (int): Number of lipids in the upper leaflet (default is 1).
        """
        prevs = [i.get_attribute('value') for i in self.driver.find_elements(By.XPATH, '//input[starts-with(@value, "PEG")]')]
        if len(prevs) != 0:
            prev = sorted(set(prevs))[-1][-1]
            new = chr(ord(prev) + 1).upper()
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
        try:
            u = self.driver.find_element(By.NAME, f'lipid_ratio[upper][peg{new_l}]')
            u.clear()
            u.send_keys(upper)
            l = self.driver.find_element(By.NAME, f'lipid_ratio[lower][peg{new_l}]')
            l.clear()
            l.send_keys(lower)
        except:
            u = self.driver.find_element(By.NAME, f'lipid_number[upper][peg{new_l}]')
            u.clear()
            u.send_keys(upper)
            l = self.driver.find_element(By.NAME, f'lipid_number[lower][peg{new_l}]')
            l.clear()
            l.send_keys(lower)

    def add_glycolipid(self, GRS, upper=1, lower=1):
        """
        Adds glycolipids to the system.

        Parameters:
            GRS (str): GRS input string.
            upper (int): Number of lipids in the upper leaflet (default is 1).
            lower (int): Number of lipids in the lower leaflet (default is 1).
        """
        # prevs = [i.get_attribute('value') for i in self.driver.find_elements(By.XPATH, '//input[starts-with(@value, "GLP")]')]
        # prevs = [i.get_attribute('onclick') for i in self.driver.find_elements(By.XPATH, '//input[starts-with(@value, "GLP")][@type="button"]')]
        # print(prevs)
        # self.driver.find_element(By.ID, 'add_number_gl').click()
        # prevs = [i.get_attribute('onclick') for i in self.driver.find_elements(By.XPATH, '//input[starts-with(@value, "GLP")][@type="button"]')]
        # print(prevs)
        # self.driver.find_element(By.ID, 'add_number_gl').click()
        # if len(prevs) != 0:
        #     prev = sorted(set(prevs))[-1][-1]
        #     new = chr(ord(prev) + 1).upper()
        #     row  = len(prev)
        # else:
        #     new = 'A'
        #     row  = 1
        # new_l = new.lower()
        # try:
        #     self.driver.find_element(By.ID, 'add_ratio_gl').click()
        # except:
        #     self.driver.find_element(By.ID, 'add_number_gl').click()

        prevs = [i.get_attribute('value') for i in self.driver.find_elements(By.XPATH, '//input[starts-with(@value, "GLP")][@type="button"]')]
        prev = sorted(set(prevs))[-1][-1]
        new = chr(ord(prev) + 1).upper()
        row  = ord(new) - 64
        try:
            self.driver.find_element(By.ID, 'add_ratio_gl').click()
        except:
            self.driver.find_element(By.ID, 'add_number_gl').click()
        new_l = new.lower()

        main_window = self.driver.window_handles[0]
        element = self.driver.find_element(By.ID, "footer")
        self.driver.execute_script("arguments[0].scrollIntoView()", element)
        #element = self.driver.find_element(By.XPATH, f"//input[@type='button'][@value=\"GLP{new}\"]")
        try:
            element  = self.driver.find_element(By.CSS_SELECTOR, f"#liptype_ratio_gl > tbody:nth-child({row}) > tr:nth-child(1) > td:nth-child(1) > input:nth-child(1)")
            element.click()
        except:
            element  = self.driver.find_element(By.CSS_SELECTOR, f"#liptype_number_gl > tbody:nth-child({row}) > tr:nth-child(1) > td:nth-child(1) > input:nth-child(1)")
            element.click()
        popup = self.driver.window_handles[-1]
        self.driver.switch_to.window(popup)
        time.sleep(2)
        self.GRS_reader(GRS=GRS, skip=1)
        self.nxt()
        self.driver.switch_to.window(main_window)
        time.sleep(2)
        try:
            u = self.driver.find_element(By.NAME, f'lipid_ratio[upper][glp{new_l}]')
            u.clear()
            u.send_keys(upper)
            l = self.driver.find_element(By.NAME, f'lipid_ratio[lower][glp{new_l}]')
            l.clear()
            l.send_keys(lower)
        except:
            u = self.driver.find_element(By.NAME, f'lipid_number[upper][glp{new_l}]')
            u.clear()
            u.send_keys(upper)
            l = self.driver.find_element(By.NAME, f'lipid_number[lower][glp{new_l}]')
            l.clear()
            l.send_keys(lower)
        time.sleep(2)


    def run(self, email, password, path=None, file_name=None, screenshot=False, download_now=True, pdb_id=None, model=None, chains=None, hets=None, pH=None, preserve={'option': None}, mutations=None, protonations=None, disulfides=None, phosphorylations=None, gpi={'GRS': None}, glycans=None, orientation={'option':'PDB'}, position={'option': None}, area={'option': None}, projection={'option': None}, boxtype={'option': None}, lengthZ={'option': None}, lengthXY={'option': 'ratio', 'value': 100}, lipids=None, naas=None, pegs=None, glycolipids=None, size=100, ions='NaCl', ff='c36m', amber_options = None, engine='gmx', temp='310'):
        """
        Runs the membrane protein setup and simulation.

        Parameters:
            email (str): User's email address.
            password (str): User's password.
            path (str): Directory path where the PDB file is located (optional).
            file_name (str): Name of the PDB file (optional).
            download_now (bool): Whether to download the output immediately (default is True).
            pdb_id (str): PDB ID for fetching the file (optional).
            model (any): Model selection options (optional).
            chains (list): List of chains to be patched (optional).
            het (str): Type of non-protein molecule (optional).
            pH (float): Desired pH value (optional).
            preserve (dict): Preserve hydrogen options (default is {'option': None}).
            mutations (list): List of mutations to add (optional).
            protonations (list): List of protonations to add (optional).
            disulfides (list): List of disulfide bonds to add (optional).
            phosphorylations (list): List of phosphorylations to add (optional).
            gpi (dict): GPI anchor options (default is {'GRS': None}).
            glycans (list): List of glycans to add (optional).
            orientation (str): Orientation option (default is 'PDB').
            position (dict): Position options (default is {'option': None}).
            area (dict): Area options (default is {'option': None}).
            projection (dict): Projection options (default is {'option': None}).
            boxtype (dict): Box type options (default is {'option': None}).
            lengthZ (any): Length in Z direction options (optional).
            lipids (list): List of lipids to add (optional).
            naas (list): List of N-acylated amino acids to add (optional).
            pegs (list): List of PEG lipids to add (optional).
            glycolipids (list): List of glycolipids to add (optional).
            size (int): Size of the system (default is 100).
            ions (str): Ion type (default is 'NaCl').
            ff (str): Force field type (default is 'c36m').
            amber_options (dict): AMBER FF options (default is None).
            engine (str): Simulation engine (default is 'gmx').
            temp (float): Temperature in Kelvin (default is 310).
        """
        try:
            self.login(email, password)
            self.wait_text("Protein/Membrane System")
            time.sleep(2)
            if file_name is not None:
                self.upload(file_name, path)
            else:
                self.from_pdb(pdb_id)

            # self.wait_text("Model/Chain Selection Option")
            # jobid = self.driver.find_element(By.CLASS_NAME, "jobid").text
            # print(jobid)
            # self.model_select(model)
            # self.nxt()
            # self.wait_text("PDB Manipulation Options")
            jobid = self.manipulate_PDB(path, file_name, pdb_id, model, chains, hets, pH, preserve, mutations, protonations, disulfides, phosphorylations, gpi, glycans)

            # if chains is not None:
            #     for chain in chains:
            #         self.patch(chain[0], chain[1], chain[2])
            # if het is not None:
            #     self.read_het(het, source, gen_with, lig_filename, ph_ligand)
            # self.system_pH(pH)
            # self.preserve(**preserve)
            # if mutations is not None:
            #     for mutation in mutations:
            #         self.add_mutation(**mutation)
            # if protonations is not None:
            #     for protonation in protonations:
            #         self.add_protonation(**protonation)
            # if disulfides is not None:
            #     for disulfide in disulfides:
            #         self.add_disulfide(**disulfide)
            # if phosphorylations is not None:
            #     for phosphorylation in phosphorylations:
            #         self.add_phosphorylation(**phosphorylation)
            # self.add_gpi(**gpi, skip=6)
            # if glycans is not None:
            #     for glycan in glycans:
            #         self.add_glycan(**glycan, skip=1)
            self.nxt(prev_step="PDB Manipulation", screen=screenshot, jobid=jobid)
            self.wait_text("Area Calculation Options")
            self.orientation(**orientation)
            self.position(**position)
            self.area(**area)
            self.nxt(prev_step="Orientation Options", screen=screenshot, jobid=jobid)
            self.wait_text('default surface area')
            self.projection(**projection)
            self.box_type(**boxtype)
            self.lengthZ(**lengthZ)
            self.lengthXY(**lengthXY)
            if lipids is not None:
                for lipid in lipids:
                    self.add_lipid(**lipid)
            if naas is not None:
                for naa in naas:
                    self.add_naa(**naa)
            if pegs is not None:
                for peg in pegs:
                    self.add_peg(**peg)
            if glycolipids is not None:
                for glycolipid in glycolipids:
                    self.add_glycolipid(**glycolipid)
            self.show_system_info()
            time.sleep(2)
            self.wait_text('Calculated XY System Size')
            self.nxt(prev_step="Lipid Options", screen=screenshot, jobid=jobid)
            time.sleep(10)
            try:
                WebDriverWait(self.driver, 30).until(EC.alert_is_present()) #,
                                            #'Timed out waiting for PA creation ' +
                                            #'confirmation popup to appear.')

                self.driver.switch_to.alert.accept()
                message = '''The alert
                'There is an issue on system size calculation. You may want to choose other method to resolve this issue. Do you want to proceed?'
                was accepted. Please check the output thoroughly.
                '''
                print(message)
            except:
                pass
            self.wait_text("Component Building Options")
            self.clear_ion()
            self.add_ion('NaCl')
            self.driver.find_element(By.XPATH, "//*[starts-with(@onclick, 'update_nion')]").click()
            self.nxt(prev_step="Component Building Options", screen=screenshot, jobid=jobid)
            self.wait_text('Building Ion and Waterbox')
            self.nxt(prev_step="Building Ion and Waterbox", screen=screenshot, jobid=jobid)
            self.wait_text('Assemble Generated Components')
            self.nxt(prev_step="Assemble Generated Components", screen=screenshot, jobid=jobid)
            self.wait_text("Force Field Options")
            self.force_field(ff, amber_options)
            self.engine(engine)
            self.temperature(temp)
            self.nxt(prev_step="Force Field Options", screen=screenshot, jobid=jobid)
            self.wait_text("Equilibration Input Notes")
            if download_now:
                print(f'Ready to download from retrieve job id {jobid}')
                self.download(jobid)
                self.driver.quit()
                print(f'Job done - output under \"{self.path_out}charmm-gui-{jobid.split(" ")[-1]}\"')
            else:
                self.driver.quit()
                print(f'Job done, but has not been retrieved - JOBID: {jobid.split(" ")[-1]}')
        except:
            traceback.print_exc()
            print('Exception raised')
            self.driver.quit()

class Membrane(MembraneProtein):
    """
    Membrane setup simulation.
    """

    def run(self, email, password, download_now=True, screenshot=False, boxtype=None, lengthZ=None, lengthXY={'option': 'ratio', 'value': 200}, lipids=None, naas=None, pegs=None, glycolipids=None, size=100, ions='NaCl', ff='c36m', amber_options=None, engine='gmx', temp='310'):
        """
        Runs the membrane setup and simulation.

        Parameters:
            email (str): User's email address.
            password (str): User's password.
            download_now (bool): Whether to download the output immediately (default is True).
            boxtype (dict): Box type options (optional).
            lengthZ (any): Length in Z direction options (optional).
            lipids (list): List of lipids to add (optional).
            naas (list): List of N-acylated amino acids to add (optional).
            pegs (list): List of PEG lipids to add (optional).
            glycolipids (list): List of glycolipids to add (optional).
            size (int): Size of the system (default is 100).
            ions (str): Ion type (default is 'NaCl').
            ff (str): Force field type (default is 'c36m').
            amber_options (dict): AMBER FF options (default is None).
            engine (str): Simulation engine (default is 'gmx').
            temp (float): Temperature in Kelvin (default is 310).
        """
        try:
            self.login(email, password)
            self.wait_text("Protein/Membrane System")
            self.driver.find_element(By.XPATH, '//a[@href="#"]').click()
            self.wait_text('default surface area')
            jobid = self.driver.find_element(By.CLASS_NAME, "jobid").text
            print(jobid)
            self.lengthXY(**lengthXY)
            if lipids is not None:
                for lipid in lipids:
                    self.add_lipid(**lipid)
            if naas is not None:
                for naa in naas:
                    self.add_naa(**naa)
            if pegs is not None:
                for peg in pegs:
                    self.add_peg(**peg)
            if glycolipids is not None:
                for glycolipid in glycolipids:
                    self.add_glycolipid(**glycolipid)
            self.show_system_info()
            time.sleep(2)
            self.wait_text('Calculated XY System Size')
            self.nxt(prev_step="Lipid Options", screen=screenshot, jobid=jobid)
            time.sleep(10)
            try:
                WebDriverWait(self.driver, 30).until(EC.alert_is_present()) #,
                                            #'Timed out waiting for PA creation ' +
                                            #'confirmation popup to appear.')

                self.driver.switch_to.alert.accept()
                message = '''The alert
                'There is an issue on system size calculation. You may want to choose other method to resolve this issue. Do you want to proceed?'
                was accepted. Please check the output thoroughly.
                '''
                print(message)
            except:
                pass
            # There is an issue on system size calculation. You may want to choose other method to resolve this issue. Do you want to proceed?
            self.wait_text("Component Building Options")
            self.clear_ion()
            self.add_ion('NaCl')
            self.driver.find_element(By.XPATH, "//*[starts-with(@onclick, 'update_nion')]").click()
            self.nxt(prev_step="Component Building Options", screen=screenshot, jobid=jobid)
            self.wait_text('Building Ion and Waterbox')
            self.nxt(prev_step="Building Ion and Waterbox", screen=screenshot, jobid=jobid)
            self.wait_text('Assemble Generated Components')
            self.nxt(prev_step="Assemble Generated Components", screen=screenshot, jobid=jobid)
            self.wait_text("Force Field Options")
            self.force_field(ff, amber_options)
            self.engine(engine)
            self.temperature(temp)
            self.nxt(prev_step="Force Field Options", screen=screenshot, jobid=jobid)
            self.wait_text("Equilibration Input Notes")
            if download_now:
                print(f'Ready to download from retrieve job id {jobid}')
                self.download(jobid)
                self.driver.quit()
                print(f'Job done - output under \"{self.path_out}charmm-gui-{jobid.split(" ")[-1]}\"')
            else:
                self.driver.quit()
                print(f'Job done, but has not been retrieved - JOBID: {jobid.split(" ")[-1]}')
        except:
            traceback.print_exc()
            print('Exception raised')
            self.driver.quit()

def main(system_type):
    """
    Main function to run the simulation based on the system type.

    Parameters:
        system_type (str): Type of the system to run ('SP', 'MP', 'M', 'R', 'PR', 'FC', 'RC').
    """
    if system_type == 'SP':
        SolutionProtein(system='solution', **parsed_yaml['system_info']).run(**parsed_yaml['details'])
    elif system_type == 'MP':
        MembraneProtein(system='membrane', **parsed_yaml['system_info']).run(**parsed_yaml['details'])
    elif system_type == 'M':
        Membrane(system='membrane', **parsed_yaml['system_info']).run(**parsed_yaml['details'])
    elif system_type == 'R':
        Retrieve(system='retrieve', **parsed_yaml['system_info']).run(**parsed_yaml['details'])
    elif system_type == 'PR':
        PDBReader(system='reader', **parsed_yaml['system_info']).run(**parsed_yaml['details'])
    elif system_type == 'FC':
        FFConverter(system='converter', **parsed_yaml['system_info']).run(**parsed_yaml['details'])
    elif system_type == 'RC':
        PDBReaderFFConverter(system='readerconverter', **parsed_yaml['system_info']).run(**parsed_yaml['details'])
    else:
        print('System type must be specified')

def create_arg_parser():
    """
    Creates and returns the argument parser for the script.

    Returns:
        parser (argparse.ArgumentParser): Argument parser object.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help='Script to automate CharmmGui process.')
    parser.add_argument('-i', '--input', help='Input yaml name', default='input.yaml')

    # Allows one to set the email from the program call to avoid having to write it to any files
    parser.add_argument('-e', '--email', help='Email to use when logging in to charmm-gui', default=False)
    
    # Allows one to set the password from the program call to avoid having to write it to any files
    parser.add_argument('-pw', '--password', help='Password to use when logging in to charmm-gui', default=False)

    return parser

if __name__ == "__main__":
    parser = create_arg_parser()
    args = parser.parse_args()
    input_file = args.input
    input_email = args.email
    input_password = args.password
    with open(input_file, 'r') as stream:
        parsed_yaml = yaml.safe_load(stream)
    
    # Overwrites email from yaml file if given using the terminal
    if input_email:
        parsed_yaml["details"]["email"] = input_email

    # Overwrites password from yaml file if given using the terminal
    if input_password:
        parsed_yaml["details"]["password"] = input_password
    
    # Prints a safer version of the yaml settings with the password changed to "******"
    parsed_yaml_safe = copy.deepcopy(parsed_yaml)
    if "details" in parsed_yaml_safe:
        if "password" in parsed_yaml_safe["details"]:
            parsed_yaml_safe["details"]["password"] = "******"
    print(parsed_yaml_safe)
    
    main(**parsed_yaml['system_type'])
