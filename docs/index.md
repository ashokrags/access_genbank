# **Access Genbank**

## **Summary**
This is a guide to using the `Access Genbank` script for downloading data from NCBI genbank in a organized manner to enable reproducibility, as well as to provide a simple interface for bulk downloads from NCBI's Genbank databases.
## **Quickstart**


## **Motivation**
A primary objective of the [Computational Biology Core](https://cbc.brown.edu) at Brown's [Centre for Computational Biology of Human Disease](https://www.brown.edu/research/projects/computational-biology-of-human-disease/home), is to enable reproducibility in computational analysis of NGS data. Here we provide a simple tool for downloading data from Genbank in an organized manner. This is mainly useful in the context of trying to download multiple genomes, since data within Genbank is not structured in a similar fashion. 

## **Overview**
**Access Genbank** is an user-friendly python script to download genomes from Genbank. The user is expected to not have any programming knowledge and needs to only provide a control file in a YAML format, chosen for its human readability.  The tool is developed to alleviate some of the primary issues with scaling up pipelines, such as file naming, management of data, output and logs. The main aim was to generate screen databases of genomes for tools such as Fastq Screen, Kraken etc which require multiple genomes or sets of genomes for usage.

## **How it works**
This is a pure python script and uses the `FTP` library to download data from Genbank and the logging module for comprehensive logs. 

## **Key Features**
We will describe some key features for downloading using the set of bacerial genomes from NCBI as an example use case.

- **Download multiple genomes** : Get all the bacterial genomes
- **Download only a specific set of genomes**: Here you can provide a list of the Bacterial species that you would like to download
- **Exclude a specific set of genomes**: This is a list of species that you specify not be included in the complete set of Bacterial genomes

In addition this provides a comprehensive log of what was downloaded for the given set
