#  Rasa Chat Bot

## Version Information

```
Rasa Version     : 2.3.0
Rasa SDK Version : 2.3.1
Rasa X Version   : None
Python Version   : 3.7.9
Operating System : Windows-10-10.0.19041-SP0
```

## Environment Setup

```
conda create rasa
conda activate rasa
pip install rasa 
pip install rasa[Spacy]
pip install pandas
python -m spacy download en_core_web_md
python -m spacy link en_core_web_md en
```

## Dev and Test

```
rasa data validate
rasa train
rasa run actions
rasa shell
```
