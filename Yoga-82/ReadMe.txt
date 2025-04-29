This repository contains: 
1> Train and test split
	yoga_train.txt
	yoga_test.txt

Each of the split text file structure
row-> each row corresponds to each sample detail
col-> <image_address+name> , <label of class_6> , <label of class_20> , <label of class_82>

2> 82 text files correspond to each of the yoga pose with  
row-> each row corresponds to each sample detail
col-> <image_address+name> , <url>

Save the images in same <folder/image> name as given in 82 text files.


Please cite the following paper if you use this dataset.

@article{verma2020yoga,
  title={Yoga-82: A New Dataset for Fine-grained Classification of Human Poses},
  author={Verma, Manisha and Kumawat, Sudhakar and Nakashima, Yuta and Raman, Shanmuganathan},
  journal={arXiv preprint arXiv:2004.10362},
  year={2020}
}
