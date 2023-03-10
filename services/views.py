from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from .dbinit.initiation import dbinit, jobkoreainit, question_type_init, company_init, major_large_init, major_small_init, job_large_init, job_small_init, recommend_type_init, school_init, doc_init, answer_init, sample_init
from django.contrib.auth import get_user_model

from .models import (QuestionType, Company, MajorLarge, MajorSmall, JobLarge,
                     JobSmall, RecommendType, Document, Answer, Sample,ContentList,
                     MajorList, SchoolType, JobList,Sample,AnswerList,
                     DocumentRefreshList,AnswerRefreshList)
from .serializers import ContentListSerializer,DocumentSerializer,AnswerSerializer,JobSmallTypeSerializer,DocumentRefreshSerializer,AnswerRefreshSerializer
from logs.models import EvalLog, RecommendLog
from inference.similarity import content_based_filtering_cosine_with_tag1

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import HttpResponse
from django.db.models import F

from django.db.models.functions import Length
from services.apps import ServicesConfig
from inference.preprocess import Recommendation
from django.core.files.storage import FileSystemStorage
import os
import os.path
import time
import json
import random
import pickle
import ast


# Create your views here.

@api_view(['POST', ])
def answer_recommend(request):
    data = request.data
    company = get_object_or_404(Company, company=data["company"])
    job_small = get_object_or_404(JobSmall, job_small_id=int(data["jobType"]))
    question_type = get_object_or_404(QuestionType, question_type_id = int(data["questionType"]))
    question_text = data["questionText"]
    content = data["content"]
    user = request.user
    rec_log_id = data["logId"]
    if question_type.question_type_id == 1000023:
        import re
        WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))
        question_text = WHITESPACE_HANDLER(question_text)
        question_category, sim = ServicesConfig.embedder.match_question_top1(question_text, ServicesConfig.question_emb_matrix)
        if len(question_text)==0 or sim < 0.5:
            return Response(status.HTTP_412_PRECONDITION_FAILED)
        question_category +=1000000
        question_type = get_object_or_404(QuestionType, question_type_id = question_category)
    
    if len(content) < 10:
        content = ""
        
    recommend = Recommendation(ServicesConfig.document, ServicesConfig.item, ServicesConfig.qcate_dict, ServicesConfig.answer_emb_matrix, ServicesConfig.embedder, 
                            question_type.question_type_id-1000000, company.company, user.favorite_company, job_small.job_large.job_large, job_small.job_small, content, 
                            12)
    
    recommend.filtering()
    tag2, tag3, tag4 = recommend.recommend_with_company_without_jobtype(), recommend.recommend_with_jobtype_without_company(), recommend.recommed_based_popularity()
    tag1 = recommend.recommend_with_company_jobtype()
    
    ###### merge #######
    ##### use feature : [['user_job_large', 'user_major_small', 'answer', 'document', 'coin_company', 
                                # 'coin_jobsmall', 'coin_question_type', 'answer_pro_good_cnt',
                                # 'answer_pro_bad_cnt', 'doc_view', 'label' ]] 
    
    answers = ServicesConfig.input_answer.copy()
    answers['answer'] = answers['answer'].apply(make_label)
    input_answers = answers[answers["answer"].isin(tag1)].reset_index()
    pool_len = len(input_answers)
    input_answers.loc[:,'user_job_large'] = user.interesting_job_large.job_large_id
    input_answers.loc[:,'user_major_small'] = user.major_small.major_small_id
    input_answers.loc[:,'coin_company'] = 0
    input_answers.loc[:,'coin_jobsmall'] = 0
    input_answers.loc[:,'coin_question_type'] = 0
    input_answers.loc[input_answers['doc_company_id'] == company.company_id,'coin_company'] = 1
    input_answers.loc[input_answers['doc_job_small_id'] == job_small.job_small_id,'coin_jobsmall'] = 1
    # ??????????????? ???????????? ??????
    for i in range(pool_len):
        answer = ServicesConfig.answer_question_types[input_answers.loc[i, 'answer']]
        if question_type.question_type_id in answer:
            input_answers.loc[i, 'coin_question_type'] = 1
    
    input_answers = input_answers[["user_job_large", "user_major_small", "answer", "document", "coin_company",
                                   "coin_jobsmall", "coin_question_type", "answer_pro_good_cnt", "answer_pro_bad_cnt", "doc_view"]]
    input_answers['user_job_large'] = input_answers['user_job_large'].astype('str').apply(make_label)
    input_answers['user_major_small'] = input_answers['user_major_small'].astype('str').apply(make_label)
    input_answers['document'] = input_answers['document'].astype('str').apply(make_label)
    input_answers['answer_pro_good_cnt'] = input_answers['answer_pro_good_cnt'].apply(good2categ)
    input_answers['answer_pro_bad_cnt'] = input_answers['answer_pro_bad_cnt'].apply(bad2categ)
    input_answers['doc_view'] = input_answers['doc_view'].apply(view2categ)

    now_answers = input_answers['answer'].values
    result = ServicesConfig.cbst.predict_proba(input_answers)[:,1]
    sim = content_based_filtering_cosine_with_tag1(now_answers, ServicesConfig.answer_emb_matrix, content, ServicesConfig.embedder)
    result_with_sim = result+sim
    
    tag1 = list(input_answers.iloc[result_with_sim.argsort()[::-1][:12],:].answer)
    
    rec_log_list = [list(map(lambda x: 'a'+str(x).zfill(6), tag1[:4])),
                    list(map(lambda x: 'a'+str(x).zfill(6), tag2[:4])),
                    list(map(lambda x: 'a'+str(x).zfill(6), tag3[:4])),
                    list(map(lambda x: 'a'+str(x).zfill(6), tag4[:4]))
    ]
    
    # ????????? ?????? ???????????? ?????? ???????????? ?????? ?????????
    Answer.objects.filter(answer_id__in=sum(rec_log_list, [])).update(user_impression_cnt=F('user_impression_cnt')+1)
    
    result = {
            " ????????? ???????????????" : tag1,
            "???????????? ????????? ?????? ???????????????" : tag2,
            "????????? ????????? ???????????????" : tag3,
            "????????? ?????? ?????????" : tag4,
            }
    
    result_keys = result.keys()
    rec_items = {key : [] for key in result_keys}
    
    for key in result:
        ran_num=12
        for i in range(ran_num):
            temp_answer = get_object_or_404(ContentList, answer_id= 'a'+str(result[key][i]).zfill(6))
            temp_answer = ContentListSerializer(temp_answer)
            rec_items[key].append(temp_answer.data)


    # ?????????????????? ????????? ????????? ???????????? ????????? ????????? ?????????
    rec_log = get_object_or_404(RecommendLog, rec_log_id=rec_log_id)
    rec_log.impressions = str(rec_log_list)
    rec_log.save()
    
    output_data = {"recommendation": rec_items, "logId": rec_log_id} 
    return Response(output_data)


@api_view(['POST', ])
def page_change(request):
    data = request.data
    now_tag = data["tagIdx"]
    answer_ids = data["answerIds"]
    rec_log_id = data["logId"]
    
    if request.user.username != 'admin':
        Answer.objects.filter(answer_id__in=answer_ids).update(user_impression_cnt=F('user_impression_cnt')+1)
    try:
        rec_log = get_object_or_404(RecommendLog, rec_log_id=rec_log_id)
        temp_impressions = ast.literal_eval(rec_log.impressions)
        temp_impressions[now_tag].extend(answer_ids)
        rec_log.impressions = str(temp_impressions)
        rec_log.save()
        
    except:
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    
    return Response(status=status.HTTP_200_OK)



@api_view(['POST', ])
def check_status(request):
    data = request.data
    
    user = get_object_or_404(get_user_model(), username=data['user_id'])
    answer = get_object_or_404(Answer, answer_id=data['answer_id'])
    is_good_eval = None
    
    good_count = EvalLog.objects.filter(answer_id=answer, favor=1).count()
    bad_count = EvalLog.objects.filter(answer_id=answer, favor=0).count()
    
    user_eval_list = list(user.answer_eval.all())
    
    try:
        _ = bool(get_object_or_404(get_user_model(), answer_scrap=answer))
        is_scrap = True
    except:
        is_scrap = False
    
    if answer in user_eval_list:
        is_eval = True
        eval_log = get_object_or_404(EvalLog, user_id=user, answer_id=answer)
        eval_status = eval_log.favor
    else:
        is_eval = False
    
    if is_eval:
        result = {"isScrap": is_scrap, "isEval": is_eval, "evalStatus": eval_status, "goodCnt": good_count, "badCnt": bad_count}
    else:
        result = {"isScrap": is_scrap, "isEval": is_eval, "goodCnt": good_count, "badCnt": bad_count}
    
    data = json.dumps(result)
    return Response(data, status=status.HTTP_200_OK)




def main(request):
    if not request.user.is_authenticated:  # ?????? ????????? ???????????? ????????? 
        return redirect("accounts:login")
        
    job_query = JobList.objects.all().order_by(Length('job_large').desc())
    question_query = QuestionType.objects.all()[0:21]
    sample_query = {}

    for i in range(1,22):
        question_type = str(1000000+i)
        samples = Sample.objects.filter(question_type_id = question_type)
        result = [json.dumps(sample.make_sample()) for sample in samples]
        random.shuffle(result)
        sample_query[question_type] = result
        
    for i in range(0,len(job_query)):
        job_query[i].id = "job_"+str(i)
        job_query[i].job_small = job_query[i].job_small.split(',')
        job_query[i].job_small_id = job_query[i].job_small_id.split(',')
    
    companies = Company.objects.all().order_by('company')

    context = {
        "job_list":job_query,
        "question_type" : question_query,
        'companies' : companies,
        "sample_list" : sample_query,
    }
    return render(request, 'services/main.html', context)

    


@api_view(['GET', ])
def search_company(request):
    companies = Company.objects.all()
    context = {
        'companies' : companies
    }

    # serializer ???????????? ???
    return render(request, 'search_test.html', context)




'''
????????? ????????? ????????????????????? ???????????? ????????????, ????????? ???????????? ?????? url??? ???????????????.
'''

def db_first(request):
    data_path = '/opt/ml/RecommendU/RecommendU-back/services/dbinit/'
    question_types, companies, major_larges, major_smalls, job_larges, job_smalls, schools, recommend_types, major_dict, job_dict = dbinit(data_path)   
    
    question_type_init(question_types)
    company_init(companies)
    major_large_init(major_larges)
    major_small_init(major_smalls, major_dict)
    job_large_init(job_larges)
    job_small_init(job_smalls, job_dict)
    recommend_type_init(recommend_types)
    school_init(schools)

    return HttpResponse("Init Done!")
 


def docu_answer_init(request):
    data_path = '/opt/ml/RecommendU/RecommendU-back/services/dbinit/'
    answer_data, doc_data, sample_data = jobkoreainit(data_path)

    doc_init(doc_data)
    answer_init(answer_data)
    sample_init(sample_data)

    return HttpResponse(f"cover letter saving Done")

# document, answer ???????????? model server??? ?????? api
@api_view(["GET"])
def document_total(request):
    queryset = Document.objects.all()
    serializer = DocumentSerializer(queryset,many=True)
    return Response(serializer.data)

@api_view(["GET"])
def answer_total(request):
    queryset = AnswerList.objects.all()
    serializer = AnswerSerializer(queryset,many=True)
    return Response(serializer.data)

@api_view(["GET"])
def job_total(request):
    queryset = JobSmall.objects.all()
    serializer = JobSmallTypeSerializer(queryset,many=True)
    return Response(serializer.data)

# ????????? refresh??? ?????? api
@api_view(["GET"])
def document_refresh(request):
    queryset = DocumentRefreshList.objects.all()
    serializer = DocumentRefreshSerializer(queryset,many=True)
    return Response(serializer.data)

@api_view(["GET"])
def answer_refresh(request):
    queryset = AnswerRefreshList.objects.all()
    serializer = AnswerRefreshSerializer(queryset,many=True)
    return Response(serializer.data)

# ??????????????? ?????? ???????????? api
@api_view(["POST"])
def save_model(request):
    data = request.data
    if data['model'] == 'CatBoost':
        model_name = 'catboost'
    elif data['model'] == 'FM':
        model_name = 'fm'
    else:
        print('model not exist')
        return Response('model not exist',status=status.HTTP_400_BAD_REQUEST) 
    model_file = data['file']
    save_path = f"./inference/models/{model_name}_model.cbm" 
    fs = FileSystemStorage()
    if os.path.isfile(save_path):
        os.remove(save_path)
    filename = fs.save(save_path, model_file)
    return Response(filename,status=status.HTTP_201_CREATED)

@api_view(["POST"])
def save_embedding(request):
    data = request.data
    answer_embed = data['answer_embedding']
    answer_question_embed = json.loads(data['question_answer_mapping_json'])
    save_path = "./inference/data/"
    fs = FileSystemStorage()
    if os.path.isfile(save_path+"answer_embedding_matrix.npy"):
        os.remove(save_path+"answer_embedding_matrix.npy")
    answer_embed_complete = fs.save(save_path+"answer_embedding_matrix.npy", answer_embed)
    if os.path.isfile(save_path+"question_cate_map_answerid.json"):
        os.remove(save_path+"question_cate_map_answerid.json")
    with open(save_path+"question_cate_map_answerid.json", 'w') as f:
        answer_question_json_complete=json.dump(answer_question_embed, f)
    return Response([answer_embed_complete,answer_question_json_complete],status=status.HTTP_201_CREATED)

@api_view(["POST"])
def save_refresh_data(request):
    data = request.data
    document_file = data['document']
    answer_file = data['answer']
    input_file = data['input']
    save_path = "./inference/data/"
    document_path = save_path+"jk_documents_3_4.csv"
    answer_path = save_path+"jk_answers_without_samples_3_4.csv"
    input_answer_path = save_path+"input_answers_1_0.csv"
    fs = FileSystemStorage()
    if os.path.isfile(document_path):
        os.remove(document_path)
    filename = fs.save(document_path, document_file)
    if os.path.isfile(answer_path):
        os.remove(answer_path)
    filename = fs.save(answer_path, answer_file)
    if os.path.isfile(input_answer_path):
        os.remove(input_answer_path)
    filename = fs.save(input_answer_path, input_file)
    return Response(filename,status=status.HTTP_201_CREATED)

def make_label(thing):
    return int(str(thing)[1:])

def view2categ(x):
    x = int(x)
    if x < 12673:
        return 0
    elif x >= 12673 and x < 25064:
        return 1
    elif x >= 25064 and x < 79171:
        return 2
    else:
        return 3


def good2categ(x):
    x = int(x)
    if x < 1:
        return 0
    elif x >= 1 and x < 2:
        return 1
    elif x >= 2 and x < 3:
        return 2
    else:
        return 3

def bad2categ(x):
    x = int(x)
    if x < 1:
        return 0
    elif x >= 1 and x < 2:
        return 1
    elif x >= 2 and x < 3:
        return 2
    else:
        return 3