from django.shortcuts import render,redirect
from GSApp.models import GSpdf
from django.contrib import messages
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from string import punctuation
from io import StringIO
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
import shutil
import os
import pandas as pd
import numpy as np
import pickle
import re


def home(request):
    dict2 ={}
    val0,val1,val2,val3,valf =[],[],[],[],[]
    if request.method=='POST':
        try:
           file = request.FILES['file']
           file_name = file.name
           file_type = file_name[:2]
           if file_name.endswith(".pdf"):
               pd1 = GSpdf(pdf = file)
               pd1.save()
           else:
                messages.error(request,"You have selected wrong file type!! this system only excepted PDF file")
                return redirect("/")   
        except Exception:
            messages.error(request,"You have not selected any file yet!!!")
            return redirect("/")
    else:
        return render(request,'home.html')
    
    max_words = 1000
    max_len = 150

    def Question(txt,key,Ans,dic,num):
        Q_start = findnth(txt,key, 0) ##### finding 'Marked Out of to start question'
        # print("Q_start:",Q_start)

        Ques = txt[Q_start:].split('Saved:')[0] #### splitting from Saved to remove all answers from question
        Ques = Ques.replace("-",' ') ##### replacing '-' by white space because it was creating problem when splited and 
        Ans = Ans.replace("-",' ') ###### and joind again for further processing
        Ques = listToString(Ques.split())##### splitted and rejoind to remove all white space from question and answer
        Ans = listToString(Ans.split())

        if len(Ans)>0: 
            Ques = Ques.replace("'",'') #### replace all aposhtrophe from question because answer already remove it(technical issue)
            half = Ans[:150]  ############# starting 150 caracters are exrtacted from answer string
            
            dic['Question_'+str(num)] = Ques.split(half)[0] ##### 150 answer string is used to split the question string as to seperate question and real answer

                        
        elif len(Ans) == 0: ###### Incase there is no answer provided, then search for Response History, State Marks or the link whichever meets first
            if 'Response history' in Ques:
                dic['Question_'+str(num)] = Ques.split('Response history')[0]
            elif  'State Marks' in Ques:
                dic['Question_'+str(num)] = Ques.split('Response history')[0]
            else : 
                dic['Question_'+str(num)] = Ques.split('https://lms.lrnglobal.org')[0]

    def Answer(txt,key,dic,num):
        Ans =' '
        pick = txt.count('Saved:')
        if pick!=0:
            Ans1 = txt.split('Saved:')[pick]
            Ans = find_ans(Ans1.split())
            dic['Answer_'+str(num)] = Ans           
        Question(txt,'Marked out of',Ans,dic,num)           
        return Ans.split()

    def find_ans(Ans):
        s = ''
        for ele in Ans:
            if (ele =='3'and Ans[Ans.index(ele)+3]=='Attempt' and Ans[Ans.index(ele)+4]=='ﬁnished') or (ele =='State' and Ans[Ans.index(ele)+1]=='Marks' ):
                break
            else :
                s+=' '+ele
        match = re.search(r'\d+/\d{2}/\d{2}', s)
        # print("match",match)
        if match is not None:
            return s.split(match.group())[0]
        return s

    def listToString(s):         
        # initialize an empty string 
        str1 = " " 
        # return string   
        return (str1.join(s)) 

    ##### to find the nth substring in a string #######
    def findnth(string, substring, n):
        parts = string.split(substring, n + 1)
        if len(parts) <= n + 1:
            return -1
        return len(string) - len(parts[-1]) - len(substring)

    ##### to convert pdf into raw text and text file
    def pdf_to_text(pdfname):
        rsrcmgr = PDFResourceManager()
        sio = StringIO()
        
        laparams = LAParams()
        device = TextConverter(rsrcmgr, sio,laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        fp = open(path+pdfname, 'rb')
        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)            
        fp.close()        
        text = sio.getvalue()
        text=text.replace(chr(272)," ")
        return text
    path = ".//media//pdf//"
    d = {'Name':np.NAN,'Roll_no':np.NAN, 'Date_Time':np.nan, 'Started_on':np.nan, 'Completed_on':np.nan, 'Time_taken':np.nan, 'Question_1':np.nan, 'Answer_1':np.nan,'Question_2':np.nan,'Answer_2':np.nan,'Grade':np.nan,'Marks':np.nan}
    Data_Frame = pd.DataFrame(columns = ['Name','Roll_no', 'Date_Time', 'Started_on', 'Completed_on', 'Time_taken', 'Question_1', 'Answer_1','Question_2','Answer_2','Grade','Marks'])
    empty_files = []
    files = os.listdir(path)

    in_progress_file = []
    c=1000
    for names in files:
        if names.endswith(".pdf"):
            c+=1
            dic ={'Name':np.NAN,'Roll_no':np.NAN, 'Date_Time':np.nan, 
                'Started_on':np.nan, 'Completed_on':np.nan, 'Time_taken':np.nan, 
                'Question_1':np.nan, 'Answer_1':np.nan,'Question_2':np.nan,'Answer_2':np.nan,
                'Grade':np.nan,'Marks':np.nan}
            #### Extract Roll no. from pdf's name
            n =''
            # some changes by Mehboob
            if '_' in names:
                names1 = names.replace('_',' ')
                x = re.findall("\d", names1.split()[1])
            else:
                x = re.findall("\d", names.split()[1])
            for e in x:
                n+=e
            dic['Roll_no'] = n
            Text = pdf_to_text(names) #### extracting text from pdfs
            if 'Started on' and 'Time taken' not in Text: ##### if some pointers like time taken and started on is not available in the pdf file then move that file into misfits folder
                shutil.move(path+names,'misfits')
                continue
            #### to check if Status is not in progress, if state of the pdf is in progress then don't do anything 
            splitted_ny_nl = Text.split('\n')
            if splitted_ny_nl[8]=='State In progress':
                in_progress_file.append(names)
                shutil.move(path+names,'misfits')
                continue
            dic['Name'] = splitted_ny_nl[4]            
            dic['Date_Time'] = splitted_ny_nl[6].split(',')[1]
            dic['Started_on'] = splitted_ny_nl[6].split(',')[2]
            dic['Completed_on'] = splitted_ny_nl[10].split(',')[2]
            dic['Time_taken'] = splitted_ny_nl[12].split('taken')[1]
            txt = pdf_to_text(names)
            #### Data splitted Question wise, in order to save mixing
            first_half = txt.split('Question\n2')[0] ### this is first question and first answer 
            second_half = txt.split('Question\n2')[1]### this is second question with 2nd answer
            Ans1 = Answer(first_half,'Saved:',dic,1)
            Ans2 = Answer(second_half,'Saved:',dic,2)
            Data_Frame = Data_Frame.append(dic,ignore_index = True)
            os.remove(path+names)
    Data_Frame.to_csv(path+'pdf_2_csv_file.csv',index = False)
    

    ############################################################### 

    #Unpickling
    models = []
    predictions = []
    ######## Loading all pretrained models
    if file_type == "B2":
        print("B2")
        model_0 = pickle.load(open(".//media//PickleFiles//B2//B2_model_0.pickle.dat", "rb"))
        model_1 = pickle.load(open(".//media//PickleFiles//B2//B2_model_1.pickle.dat", "rb"))
        model_2 = pickle.load(open(".//media//PickleFiles//B2//B2_model_2.pickle.dat", "rb"))
        model_3 = pickle.load(open(".//media//PickleFiles//B2//B2_model_3.pickle.dat", "rb"))
    elif file_type == "C1":
        print("C1")
        model_0 = pickle.load(open(".//media//PickleFiles//C1//C1_model_0.pickle.dat", "rb"))
        model_1 = pickle.load(open(".//media//PickleFiles//C1//C1_model_1.pickle.dat", "rb"))
        model_2 = pickle.load(open(".//media//PickleFiles//C1//C1_model_2.pickle.dat", "rb"))
        model_3 = pickle.load(open(".//media//PickleFiles//C1//C1_model_3.pickle.dat", "rb"))
    elif file_type == "C2":
        print("C2")
        model_0 = pickle.load(open(".//media//PickleFiles//C2//C2_model_0.pickle.dat", "rb"))
        model_1 = pickle.load(open(".//media//PickleFiles//C2//C2_model_1.pickle.dat", "rb"))
        model_2 = pickle.load(open(".//media//PickleFiles//C2//C2_model_2.pickle.dat", "rb"))
        model_3 = pickle.load(open(".//media//PickleFiles//C2//C2_model_3.pickle.dat", "rb"))
    else:
        messages.error(request,"You have selected wrong file formate!!")
        return redirect("/")   
    def predict_val(answer):
        predictions =0
        input = open(".//media//PickleFiles//tokenizer.pkl", "rb")
        tokenizer = pickle.load(input)
        
        test_sequences = tokenizer.texts_to_sequences(answer)
        test_sequences_matrix = sequence.pad_sequences(test_sequences,maxlen=max_len)
        val0.append(model_0.predict(test_sequences_matrix)[0])
        val1.append(model_1.predict(test_sequences_matrix)[0])
        val2.append(model_2.predict(test_sequences_matrix)[0])
        val3.append(model_3.predict(test_sequences_matrix)[0])
        dict2["OverallImpression"]=val0 
        dict2["TaskFulfilment"]=val1
        dict2["OrganisationAndCohesion"]=val2 
        dict2["GrammarAndLexis"]=val3
        
        

        predictions += (model_0.predict(test_sequences_matrix)+
                        model_1.predict(test_sequences_matrix)+
                        model_2.predict(test_sequences_matrix)+
                        model_3.predict(test_sequences_matrix))
        valf.append(predictions[0])
        dict2["Predictions"]= valf
        return predictions
    data = pd.read_csv(path+'pdf_2_csv_file.csv')
    result=predict_val(data['Answer_1'])+predict_val(data['Answer_2'])
    sr_to_dictRoll =data['Roll_no'].to_dict()
    sr_to_dictName =data['Name'].to_dict()
    dict2["result"] = result[0]
    dict2["Roll_No"]= sr_to_dictRoll[0]
    dict2["Name"]= sr_to_dictName[0]
    # print("dict2",dict2)
    messages.success(request,'result will be display on window')
    return render(request,'home.html',{"dict2":dict2})
