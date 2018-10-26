import ftputil
import logging
import os, sys
import subprocess as sp

logging.basicConfig(filename='download_app.log', filemode='w', format='%(levelname)s - %(message)s',
                    level=logging.DEBUG)

# https://warwick.ac.uk/fac/sci/moac/people/students/peter_cock/python/ftp/


# base_path = sys.argv[1]





class GenbankAccessor:
    files_downloaded = []
    species_retrieved = []
    download_info = dict()
    assembly_dir = ''

    def __init__(self, base_ftp_path = '/genomes/refseq/bacteria',
                 assembly_dir = 'latest_assembly_versions',
                 file_type_to_search='genomic.fna',
                 species_to_exclude=["Abiotrophia_sp._HMSC24B09"],
                 concatenate=False,
                 output_dir = None,
                 dry_run = False):
        self.base_ftp_path = base_ftp_path
        self.assembly_dir = assembly_dir
        self.species_to_exclude = species_to_exclude
        self.target_species_list = []
        self.out_dir = output_dir
        self.file_type_to_search = file_type_to_search
        self.concatenate = concatenate
        self.connect()
        self.create_species_download_list()
        self.create_download_genomes_list()
        if not dry_run:
            self.download_genomes()

        return



    def connect(self):
        self.host = ftputil.FTPHost('ftp.ncbi.nlm.nih.gov', 'anonymous', 'password')
        self.host.chdir(self.base_ftp_path)
        logging.info("Number of Genomes to Fetch: " + str(len(self.host.listdir("."))))
        return

    def create_species_download_list(self):
        if len(self.target_species_list) > 0 and len(self.species_to_exclude) > 0:
            print "Error. You can only specify one or the other\n"
            sys.exit(0)
        else:
            dir_list = self.host.listdir(".")
            if len(self.species_to_exclude) > 0:
                self.species_retrieved = [x for x in dir_list if x not in self.species_to_exclude]
            elif len(self.target_species_list) > 0:
                self.species_retrieved = self.target_species_list
            else:
                self.species_retrieved = [x for x in dir_list]
        return

    def create_download_genomes_list(self):
        for species in self.species_retrieved[:5]:
            print species
            ##if species in species_to_exclude:
            ##    print "found species to exclude"

            species_rtrv_path = os.path.join(self.base_ftp_path, species)
            self.host.chdir(species_rtrv_path)
            print self.host.listdir(".")

            if self.assembly_dir in self.host.listdir("."):

                tmp_final_path = os.path.join(species_rtrv_path, self.assembly_dir)
                # print tmp_final_path
                self.host.chdir(tmp_final_path)

                if len(self.host.listdir(".")) > 1:
                    info_txt = species + ": There are multiple assemblies\n\tAssemblies: "
                    info_txt += ', '.join(self.host.listdir("."))
                    info_txt += "\n\tUsing the Latest Assembly: " + self.host.listdir(".")[-1]
                    logging.warning(info_txt)
                    tmp_final_path += "/" + self.host.listdir(".")[-1]
                else:

                    tmp_final_path += "/" + self.host.listdir(".")[0]

                # change into the assembly directory
                self.host.chdir(tmp_final_path)

                download_file_path = ''

                if self.file_type_to_search == "genomic.fna":
                    download_files_idx_list = [i for i, s in enumerate(self.host.listdir(".")) if
                                               self.file_type_to_search in s]
                    tmp_list_files = [self.host.listdir(".")[x] for x in download_files_idx_list]
                    download_file_idx = [i for i, s in enumerate(tmp_list_files) if 'from_genomic' not in s]
                    file_to_retr = tmp_list_files[download_file_idx[0]]
                    download_file_path = os.path.join(tmp_final_path, file_to_retr )
                else:
                    download_file_idx = [i for i, s in enumerate(self.host.listdir(".")) if self.file_type_to_search in s][0]
                    print self.host.listdir(".")[download_file_idx[0]]
                    file_to_retr = self.host.listdir(".")[download_file_idx[0]]
                    download_file_path = os.path.join(tmp_final_path, file_to_retr )
                com = "wget ftp://"
                com +=  download_file_path + " "
                self.download_info[species] = {'Available': True, 'download_path': download_file_path, 'file_to_retr': file_to_retr, 'wget_command': com}
            else:
                logging.warning(species + ": Assembly not found .. Skipping")
                self.download_info[species] = {'Available': False}
        return

    def download_genomes(self):
        #sp.check_output(com, shell=True)
        if self.out_dir is not None:
            down_dir = self.out_dir
        else:
            down_dir = os.getcwd()

        concat_file = self.base_ftp_path.split("/")[-1] + "_concat.fa"

        for spp,v in self.download_info.iteritems():
            if not v['Available']:
                continue
            else:
                file_to_retr = v['file_to_retr']
                if self.host.path.isfile(v['download_path']):
                    self.host.download(v['download_path'], os.path.join(down_dir,file_to_retr))
                    if self.concatenate:
                        com = "gunzip -c " + os.path.join(down_dir,file_to_retr) + " | sed 's/>/>" + spp + "_/' >> "
                        com += os.path.join(down_dir, concat_file )
                        sp.check_output(com, shell=True)

        if self.concatenate and os.path.exists(os.path.join(down_dir, concat_file)):
            sp.check_output( "gzip " + os.path.join(down_dir,concat_file) , shell=True)
        return

if __name__== "__main__" :
    GenbankAccessor( concatenate=True)