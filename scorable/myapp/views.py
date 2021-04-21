from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Albam, Score
from .forms import AlbamForm, ScoreForm, UserEditForm
from accounts.forms import CustomUser
from scorable.settings import MEDIA_ROOT
import os.path
import copy #リストの参照無しコピー

def index(request):
    posts = Albam.objects.filter(uploaded_at__lte=timezone.now()).order_by('uploaded_at')
    return render(request, 'myapp/index.html', {'posts':posts})

def user_detail(request, pk):
    posts = Albam.objects.filter(artist_id=pk)
    my = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = UserEditForm()
    return render(request, 'myapp/user_detail.html', {'posts': posts, 'my': my, 'form':form})

def create_score(request):
    if request.method == 'POST':
        a_form = AlbamForm(request.POST, request.FILES)
        s_form = ScoreForm(request.POST, request.FILES)
        if a_form.is_valid() and s_form.is_valid():
            albam = a_form.save(commit=False)
            score = s_form.save(commit=False)
            albam.artist = request.user
            albam.save()
            score.albam = albam
            score.save()
            return redirect('score_detail', pk=score.pk)
    else:
        a_form = AlbamForm()
        s_form = ScoreForm()
    return render(request, 'myapp/create_score.html', {'a_form': a_form, 's_form':s_form})

#可変長16進数を2進数str変換
def vlen(hoge, i):
    if i == 16:
        hoge = int(hoge, 16)
        hoge2 = ''
        for i in range(7):
            if hoge % 2 == 1:
                hoge2 += '1'
                hoge = (hoge-1)/2
            else:
                hoge2 += '0'
                hoge /= 2
        fin = hoge2[::-1]
    return fin
            

def score_detail(request, pk):
    score = get_object_or_404(Score, pk=pk)
    albam = get_object_or_404(Albam, pk=pk)
    path = os.path.join(MEDIA_ROOT, str(score.midifile))
    f = open(path,'rb')
    midhead = f.read(4).hex()
    mid_h_data = f.read(4).hex()
    mid_h_format = f.read(2).hex()
    mid_h_track = int(f.read(2).hex(),16) #トラック数 (0埋め削除&10進数変換)
    mid_h_time = int(f.read(2).hex(), 16) #時間方式
    midtrack = [] #トラックチャンク始まり宣言
    mid_t_data = [] #データ長 (0埋め削除&10進数変換)
    mid_t_selection = [] #演奏データ
    mid_t_note = []
    mid_t_marker = []
    mid_t_tempo = []
    mid_t_rhythm = []
    mid_t_maxdt = 0

    for i in range(mid_h_track):
        midtrack.append(f.read(4).hex())
        mid_t_data.append(int(f.read(4).hex(),16))
        mid_t_note.append([])
        mid_t_marker.append([])
        mid_t_dtime = 0

        j = 0
        #mid_t_selection.append(f.read(mid_t_data[i]).hex())
        flag = True
        while(flag):
            hoge = f.read(1).hex()
            if int(hoge, 16)>128:
                dtime = vlen(hoge, 16)
                flag2 = True
                while(flag2):
                    hoge = f.read(1).hex()
                    if int(hoge, 16) < 128:
                        flag2 = False
                    dtime += vlen(hoge, 16)
                mid_t_dtime += int(dtime, 2)
            else:
                mid_t_dtime += int(hoge, 16)
                
            hoge = f.read(1).hex()
            #ランニングステータス判定
            #if 64 > int(hoge, 16) or (int(hoge, 16) >= 128 and 192 > int(hoge, 16)):
                #hoge = 90
            if hoge == 'ff':
                hoge2 = f.read(1).hex()
                if hoge2 == '51':
                    mid_t_tempo.append([])
                    mid_t_tempo[len(mid_t_tempo)-1].append(mid_t_dtime)
                    mid_t_tempo[len(mid_t_tempo)-1].append(int(f.read(int(f.read(1).hex(), 16)).hex(), 16))
                elif hoge2 == '58':
                    mid_t_rhythm.append([])
                    mid_t_rhythm[len(mid_t_rhythm)-1].append(mid_t_dtime)
                    mid_t_rhythm[len(mid_t_rhythm)-1].append(int(f.read(int(f.read(1).hex(), 16)).hex(), 16))
                elif hoge2 == '2f':
                    if f.read(1).hex() == '00':
                        flag = False
                elif hoge2 == '03':
                    mid_t_marker[i] = f.read(int(f.read(1).hex(), 16)).hex()
                else:
                    hoge2 = f.read(int(f.read(1).hex(), 16)).hex()
            elif hoge == ('80'or'81'or'82'or'83'or'84'or'85'or'86'or'87'or'88'or'89'or'8a'or'8b'or'8c'or'8d'or'8e'or'8f'):
                mid_t_note[i].append([])
                mid_t_note[i][len(mid_t_note[i])-1].append(mid_t_dtime)
                mid_t_note[i][len(mid_t_note[i])-1].append(int(f.read(1).hex(), 16))
                mid_t_note[i][len(mid_t_note[i])-1].append(f.read(1).hex())
                mid_t_note[i][len(mid_t_note[i])-1][2] = 0
                if mid_t_maxdt < mid_t_dtime:
                    mid_t_maxdt = mid_t_dtime
            elif hoge == ('90'or'91'or'92'or'93'or'94'or'95'or'96'or'97'or'98'or'99'or'9a'or'9b'or'9c'or'9d'or'9e'or'9f'):
                mid_t_note[i].append([])
                mid_t_note[i][len(mid_t_note[i])-1].append(mid_t_dtime)
                mid_t_note[i][len(mid_t_note[i])-1].append(int(f.read(1).hex(), 16))
                mid_t_note[i][len(mid_t_note[i])-1].append(int(f.read(1).hex(), 16))
                if mid_t_maxdt < mid_t_dtime:
                    mid_t_maxdt = mid_t_dtime
            else:
                mid_t_selection.append(f.read(int(f.read(1).hex(), 16)).hex())
            j += 1

    f.close()

    #===============================================
    #ミディの開始点と終端のデルタタイムを統合
    #===============================================
    note = []
    for i in range(len(mid_t_note)):
        note.append([])
        for j in range(len(mid_t_note[i])):
            for k in range(j+1, len(mid_t_note[i])):
                if mid_t_note[i][j][1] == mid_t_note[i][k][1] and mid_t_note[i][k][2] == 0:
                    mid_t_note[i][j].append(mid_t_note[i][k][0])
                    note[i].append(mid_t_note[i][j])
                    del mid_t_note[i][k] 
                    break


    return render(request, 'myapp/score_detail.html', {
        'score': score, 
        'score_art': score.score_art,
        'albam': albam,
        'midhead': midhead,
        'mid_h_data': mid_h_data,
        'mid_h_format': mid_h_format,
        'mid_h_track': mid_h_track,
        'mid_h_time': mid_h_time,
        'midtrack': midtrack,
        'mid_t_data': mid_t_data,
        'selection': mid_t_selection,
        'tempo': mid_t_tempo, #[0]:デルタタイム [1]:4分音符のマイクロ秒
        'rhythm': mid_t_rhythm,
        'marker': mid_t_marker,
        'note': note,
        'dtime': mid_t_dtime,
        'maxdt': mid_t_maxdt,
    })

    


    



