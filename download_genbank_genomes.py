import ftputil
import logging
import os
import subprocess as sp

logging.basicConfig(filename='download_app.log', filemode='w', format='%(levelname)s - %(message)s' , level=logging.DEBUG)

# https://warwick.ac.uk/fac/sci/moac/people/students/peter_cock/python/ftp/
base_ftp_path = '/genomes/refseq/bacteria'
assembly_dir = 'latest_assembly_versions'
#base_path = sys.argv[1]
file_type_to_search = 'genomic.fna'
species_to_exclude = ["Abiotrophia_sp._HMSC24B09"]
concatenate = False
host = ftputil.FTPHost('ftp.ncbi.nlm.nih.gov', 'anonymous', 'password')
host.chdir(base_ftp_path)

dir_list = host.listdir(".")
print len(dir_list)

species_list = [x for x in dir_list if x not in species_to_exclude]

for species in species_list[:2]:
    print species
    if species in species_to_exclude:
        print "found species to exclude"
    species_path = os.path.join(base_ftp_path,species)
    host.chdir(species_path)
    print host.listdir(".")
    if assembly_dir in host.listdir("."):
        tmp_final_path = os.path.join(species_path,assembly_dir)
        #print tmp_final_path
        host.chdir(tmp_final_path)
        if len(host.listdir(".")) > 1:
            info_txt = species + ": There are multiple assemblies\n\tAssemblies: "
            info_txt += ', '.join(host.listdir("."))
            info_txt += "\n\tUsing the Latest Assembly: " + host.listdir(".")[-1]
            logging.warning(info_txt)

        tmp_final_path += "/" + host.listdir(".")[-1]
        com = "wget ftp://"
        host.chdir(tmp_final_path)
        download_file_idx = [i for i, s in enumerate(host.listdir(".")) if file_type_to_search in s][0]

        if file_type_to_search =="genomic.fna":
            download_files_idx_list = [i for i, s in enumerate(host.listdir(".")) if file_type_to_search in s]
            tmp_list_files = [host.listdir(".")[x] for x in download_files_idx_list]
            download_file_idx = [i for i, s in enumerate(host.listdir) if 'from_genomic' not in s]
            file_to_get = os.path.join(tmp_final_path, host.listdir(".")[download_file_idx[0]])

        print host.listdir(".")
        print host.listdir(".")[download_file_idx[0]]
        com += file_to_get + " "
        logging.info(species +": " + com)
        # sp.check_output(com,shell=True)
        #file_to_get = host.listdir(".")[download_file]
        #if host.path.isfile(file_to_get):
            #host.download(file_to_get, file_to_get)
