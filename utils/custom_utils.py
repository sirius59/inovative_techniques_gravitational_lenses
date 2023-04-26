import os
from shutil import copy
from astropy.io import fits
from tqdm import tqdm
import progressbar
from urllib.request import urlretrieve
import zipfile
import matplotlib.pyplot as plt
import numpy as np

pbar = None

def show_progress(block_num, block_size, total_size):
    '''
    will show a progress bar during the download
    '''
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None

def RetrieveData(URL, rootpath="./data"):
    '''
    Download the zip file from URL if not already downloaded
    and put it in the rootpath directory.
    It is then extracted in the rootpath directory.
    
    '''
    if os.path.isdir(rootpath)==False:
        os.mkdir('./data')
        
    if os.path.isfile(os.path.join(rootpath,'data.zip'))==False:
        print('Downloading archive')
        urlretrieve(URL,os.path.join(rootpath,'data.zip'),show_progress)
        with zipfile.ZipFile(os.path.join(rootpath,'data.zip'),'r') as Zip:
            for member in tqdm(Zip.infolist(), desc='Extracting '):
                try:
                    Zip.extract(member, rootpath)
                except zipfile.error as e:
                    pass
                
def new_dataset():
    if os.path.isdir('./data/new_data')==False:
        path='./data/Savary_training_set_lenses/'# path of the data directory

        ### directories for different type of files
        lensed='Lens_simulations/' # Files containing simulations of gravitational lenses
        non_lensed='LRG_only/' # Files containing lenses only (LRG type galaxies)
        lensed_source='lensed_source_only/' # Files containing only lensed galaxies (without the lens galaxy)
        RMS='Lenses/RMS/' # Files containing the RMS image
        PSF='Lenses/PSF/' # Files containing the PSF image

        ### List of every files within a directory
        files_lensed=os.listdir(path+lensed)
        files_non_lensed=os.listdir(path+non_lensed)
        files_lensed_source=os.listdir(path+lensed_source)
        files_rms=os.listdir(path+RMS)
        files_psf=os.listdir(path+PSF)

        data=[file for file in tqdm(files_lensed, desc='Checking all available files') if (file in files_non_lensed and file in files_lensed_source and file in files_rms and file in files_psf)]
    
        os.mkdir('./data/new_data')
        os.mkdir('./data/new_data/lensed')
        os.mkdir('./data/new_data/non_lensed')
        os.mkdir('./data/new_data/lensed/RMS')
        os.mkdir('./data/new_data/non_lensed/RMS')
        os.mkdir('./data/new_data/lensed/PSF')
        os.mkdir('./data/new_data/non_lensed/PSF')
        
        for file in tqdm(data,desc='copying files'): #copy of the good files in the new dataset
            copy(os.path.join(path,non_lensed,file),os.path.join('./data/new_data/non_lensed',file))
            copy(os.path.join(path,lensed,file),os.path.join('./data/new_data/lensed',file))
            copy(os.path.join(path,PSF,file),os.path.join('./data/new_data/non_lensed/PSF',file))
            copy(os.path.join(path,PSF,file),os.path.join('./data/new_data/lensed/PSF',file))
            copy(os.path.join(path,RMS,file),os.path.join('./data/new_data/non_lensed/RMS',file))
            
        for file in tqdm(data, desc='Reconstructing RMS'):#reconstruction of the rms for the lensed files
            source_path=os.path.join(path,lensed_source,file)
            rms_path=os.path.join(path,RMS,file)
            lrg_path=os.path.join(path,non_lensed,file)
    
            source,source_header=fits.getdata(source_path, header=True)
            rms,rms_header=fits.getdata(rms_path,header=True)
            lrg,lrg_header=fits.getdata(lrg_path,header=True)
    
            gain=lrg_header['GAIN']
            source_rms=source/gain
    
            total_rms=np.sqrt(rms**2+source_rms)
    
            hdu = fits.PrimaryHDU(total_rms, header=rms_header)
            hdu.writeto(os.path.join('./data/new_data/lensed/RMS',file),overwrite=True)