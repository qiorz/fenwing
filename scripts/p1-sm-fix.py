import io
p='/home/dev/ff/gecko/dom/media/MediaDecoderStateMachine.cpp'
s=io.open(p,encoding='utf-8').read()
s=s.replace('''  OHOS_SM_HLOG("video push pts=%{public}lld size=%{public}d queue=%{public}d",
               (long long)aSample->mTime.ToMicroseconds(), (int)aSample->Size(),
               (int)VideoQueue().GetSize());''',
'''  OHOS_SM_HLOG("video push pts=%{public}lld queue=%{public}d",
               (long long)aSample->mTime.ToMicroseconds(),
               (int)VideoQueue().GetSize());''')
io.open(p,'w',encoding='utf-8').write(s)
print('fixed size field')
