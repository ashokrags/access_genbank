import ftplib
import logging
import os, sys, argparse as args, tqdm
import subprocess as sp
from datetime import datetime as d

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
                 log_dir = None,
                 dry_run = False):

        logfile = "genbank_download_app.log"
        if log_dir is not None:
            logfile = os.path.join(log_dir,"genbank_download_app.log")
        logging.basicConfig(filename=logfile, filemode='w', format='%(levelname)s - %(message)s',
                            level=logging.DEBUG)

        self.base_ftp_path = base_ftp_path
        self.assembly_dir = assembly_dir
        self.species_to_exclude = species_to_exclude
        self.target_species_list = []
        self.out_dir = output_dir
        self.file_type_to_search = file_type_to_search
        self.concatenate = concatenate
        self.init_connect()
        self.create_species_download_list()
        self.host.close()
        self.create_download_genomes_list()
        if not dry_run:
            self.download_genomes()

        return



    def init_connect(self):
        self.host = ftplib.FTP('ftp.ncbi.nlm.nih.gov', 'anonymous', 'password')
        self.host.cwd(self.base_ftp_path)
        ## TO REMOVE
        #dir_list = self.get_dir_contents(self.host)

        dir_list = self.host.nlst()
        logging.info(d.now().strftime("%Y_%m_%d %H:%M:%S: ") + "Number of Genomes to Fetch: " + str(len(dir_list)))
        return

    def create_species_download_list(self):

        if len(self.target_species_list) > 0 and len(self.species_to_exclude) > 0:
            print "Error. You can only specify one or the other\n"
            sys.exit(0)
        else:

            dir_list = self.host.nlst()
            if len(self.species_to_exclude) > 0:
                self.species_retrieved = [x for x in dir_list if x not in self.species_to_exclude]
            elif len(self.target_species_list) > 0:
                self.species_retrieved = self.target_species_list
            else:
                self.species_retrieved = [x for x in dir_list]
        return


    def create_download_genomes_list(self):
        print "\n\n**** Getting the list of species to download\n"

        for species in tqdm.tqdm(self.species_retrieved):
            #print species
            ##if species in species_to_exclude:
            ##    print "found species to exclude"
            species_rtrv_path = os.path.join(self.base_ftp_path, species)
            logging.info(d.now().strftime("%Y_%m_%d %H:%M:%S: ") + species + ":" + species_rtrv_path)
            #    logging.warnings(species + ": Connection timeout\n")
            try:
                self.host.cwd(species_rtrv_path)
            except:
                self.host.close()
                self.host = ftplib.FTP('ftp.ncbi.nlm.nih.gov', 'anonymous', 'password')

            dir_list = self.host.nlst()

            if self.assembly_dir in dir_list:
                #print species, self.assembly_dir
                tmp_final_path = os.path.join(species_rtrv_path, self.assembly_dir)
                self.host.cwd(tmp_final_path)

                dir_list = self.host.nlst()

                if len(dir_list) > 1:
                    info_txt = d.now().strftime("%Y_%m_%d %H:%M:%S: ")
                    info_txt += species + ": There are multiple assemblies\n\tAssemblies: "
                    info_txt += ', '.join(dir_list)
                    info_txt += "\n\tUsing the Latest Assembly: " + dir_list[-1]
                    logging.warning(info_txt)
                    tmp_final_path = os.path.join(tmp_final_path,dir_list[-1])
                else:

                    tmp_final_path  = os.path.join(tmp_final_path, dir_list[0])
                    logging.info(d.now().strftime("%Y_%m_%d %H:%M:%S: ") + species + ": Single Assembly: " + dir_list[0] )

                # change into the assembly directory
                # To fix timeout errors just kit the files in the directory every time
                # this prevents timeouts with data connections
                # https://ftputil.sschwarzer.net/trac/ticket/79

                self.host.cwd(tmp_final_path)


                retr_file_list = self.host.nlst()

                #print " The Observed working directory is: ", tmp_final_path
                #print " The Actual working directory is: ", self.host.pwd()

                full_file_path = ''

                if self.file_type_to_search == "genomic.fna":
                    download_files_idx_list = [i for i, s in enumerate(retr_file_list) if
                                               self.file_type_to_search in s]
                    tmp_list_files = [retr_file_list[x] for x in download_files_idx_list]
                    download_file_idx = [i for i, s in enumerate(tmp_list_files) if 'from_genomic' not in s]
                    file_to_retr = tmp_list_files[download_file_idx[0]]
                    full_file_path = os.path.join(tmp_final_path, file_to_retr )
                else:
                    download_file_idx = [i for i, s in enumerate(retr_file_list) if self.file_type_to_search in s][0]
                    #print self.host.listdir(".")[download_file_idx[0]]
                    file_to_retr = retr_file_list[download_file_idx[0]]
                    full_file_path = os.path.join(tmp_final_path, file_to_retr )

                com = "wget ftp://"
                com +=  os.path.join(tmp_final_path, file_to_retr)
                self.download_info[species] = {'Available': True, 'download_path': tmp_final_path,
                                               'file_to_retr': file_to_retr, 'full_download_path':full_file_path,
                                               'alt_download_path':self.host.pwd() ,'wget_command': com}
            else:
                logging.warning(d.now().strftime("%Y_%m_%d %H:%M:%S: ") + species + ": Assembly not found .. Skipping")
                self.download_info[species] = {'Available': False}
        return

    def download_genomes(self):
        print "\n\n **** Download Started \n"
        logging.info("************\nDownload Logs\n************\n")

        if self.out_dir is not None:
            down_dir = os.path.join(self.out_dir, "genbank_downloads")
        else:
            down_dir = os.path.join(os.getcwd(),"genbank_downloads")

        if not os.path.exists(down_dir):
            os.mkdir(down_dir)

        concat_file = self.base_ftp_path.split("/")[-1] + d.now().strftime("_%Y_%m_%d_%H_%M_") + "concat.fa"

        self.host = ftplib.FTP('ftp.ncbi.nlm.nih.gov', 'anonymous', 'password')

        for spp,v in tqdm.tqdm(self.download_info.items()):
            if not v['Available']:
                continue
            else:
                file_to_retr = v['file_to_retr']
                try:
                    self.host.cwd(v['download_path'])
                except:
                    self.host.close()
                    self.host = ftplib.FTP('ftp.ncbi.nlm.nih.gov', 'anonymous', 'password')
                    self.host.cwd(v['download_path'])

                file_exists = True

                def null_call():
                    pass

                tmp_list=[]
                try:
                    self.host.dir(v['full_download_path'], tmp_list.append)
                except:
                    file_exists = False

                file_copy = os.path.join(down_dir,file_to_retr)

                if file_exists:
                    #self.host.dir(v['full_download_path'])
                    file_orig = os.path.join(v['download_path'], file_to_retr)
                    try:
                        with open(file_copy, 'w') as fp:
                            res = self.host.retrbinary('RETR ' + file_orig, fp.write)
                            if not res.startswith('226 Transfer complete'):
                                print('Download failed')
                                logging.warning(d.now().strftime("%Y_%m_%d %H:%M:%S: ") + spp + ": DDWNLOAD FAILED " + v['full_download_path'] + "\n")
                                if os.path.isfile(file_copy):
                                    os.remove(file_copy)
                            else:
                                logging.info(d.now().strftime("%Y_%m_%d %H:%M:%S: ") + spp + ": DDWNLOAD COMPLETE " + v['full_download_path'] + "\n")

                    except ftplib.all_errors as e:
                        print('FTP error:', e)
                        logging.error(d.now().strftime("%Y_%m_%d %H:%M:%S: ") + spp + ": DDWNLOAD ERROR " + v['full_download_path'] + "\n")

                    if self.concatenate:
                        com = "gunzip -c " + os.path.join(down_dir,file_to_retr) + " | sed 's/>/>" + spp + "_/' >> "
                        com += os.path.join(down_dir, concat_file )
                        sp.check_output(com, shell=True)
                else:
                    logging.warning(d.now().strftime("%Y_%m_%d %H:%M:%S: ")+ spp + ": FILE DOES NOT EXIST " + v['full_download_path'] + "\n" )

        if self.concatenate and os.path.exists(os.path.join(down_dir, concat_file)):
            concat_gzip_file = os.path.join(down_dir,concat_file)+".gz"
            if os.path.isfile(concat_gzip_file):
                os.remove(concat_gzip_file)
            sp.check_output( "cat " + os.path.join(down_dir,concat_file) + " | gzip  > " + concat_gzip_file , shell=True)
        return

def get_args():
    '''
    Use Argparse to parse command line arguments


    :return: Argument Parser
    '''

    #base_ftp_path = '/genomes/refseq/bacteria',
    #assembly_dir = 'latest_assembly_versions',
    #file_type_to_search = 'genomic.fna',
    #species_to_exclude = ["Abiotrophia_sp._HMSC24B09"],
    #concatenate = False,
    #output_dir = None,
    #dry_run = False

    parser = args.ArgumentParser()
    parser.add_argument('-b', '--base_ftp_path', default = '/genomes/refseq/bacteria', help = "provide the base path for the directories to be queried")
    parser.add_argument('-ad', '--assembly_dir', default = 'latest_assembly_versions', help = "provide the base path for the directories to be queried")
    parser.add_argument('-ft', '--file_type_to_search', default =  'genomic.fna',  help = "provide the base path for the directories to be queried")
    parser.add_argument('-se', '--species_to_exclude', default = [], help = "provide the base path for the directories to be queried")
    parser.add_argument('-c', '--concatenate', default= False,  help = "provide the base path for the directories to be queried")
    parser.add_argument('-o', '--output_dir', default = None, help = "provide the base path for the directories to be queried")
    parser.add_argument('-ol', '--log_dir', default = None, help = "provide the base path for the directories to be queried")
    parser.add_argument('-dr', '--dry_run', default = False, help = "provide the base path for the directories to be queried")
    myargs = parser.parse_args()
    return myargs

if __name__== "__main__" :
    my_args = get_args()
    print my_args
    GenbankAccessor(base_ftp_path=my_args.base_ftp_path,
                     assembly_dir=my_args.assembly_dir,
                     file_type_to_search=my_args.file_type_to_search,
                     species_to_exclude=my_args.species_to_exclude,
                     concatenate=True,
                     #concatenate=my_args.concatenate,
                     output_dir=my_args.output_dir,
                     log_dir=my_args.log_dir,
                     dry_run=my_args.dry_run)