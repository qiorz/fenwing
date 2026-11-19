import io

p = '/home/dev/ff/gecko/dom/media/MediaDecoderStateMachine.cpp'
s = io.open(p, encoding='utf-8').read()

helper = '''
// Temporary OHOS diagnostic logging (dlopen hilog, survives link flags).
#include <dlfcn.h>
#define OHOS_SM_HLOG(...)                                      \\
  do {                                                         \\
    typedef int (*OhLogPrintFn)(int, int, unsigned int, const char*, const char*, ...); \\
    static void* sH = dlopen("libhilog_ndk.z.so", RTLD_NOW);   \\
    static OhLogPrintFn sP = sH ? (OhLogPrintFn)dlsym(sH, "OH_LOG_Print") : nullptr; \\
    if (sP) { sP(0, 4, 0, "OHOSSM", __VA_ARGS__); }            \\
  } while (0)
'''

if 'OHOS_SM_HLOG' not in s:
    anchor = '#include "MediaDecoderStateMachine.h"'
    assert s.count(anchor) == 1
    s = s.replace(anchor, anchor + helper)

    # log video queue push
    old = '  VideoQueue().Push(aSample);'
    assert s.count(old) == 1
    s = s.replace(old, '''  OHOS_SM_HLOG("video push pts=%{public}lld size=%{public}d queue=%{public}d",
               (long long)aSample->mTime.ToMicroseconds(), (int)aSample->Size(),
               (int)VideoQueue().GetSize());
  VideoQueue().Push(aSample);''')

    # log MaybeStartPlayback entry
    old = 'void MediaDecoderStateMachine::MaybeStartPlayback() {'
    assert s.count(old) == 1
    s = s.replace(old, old + '''
  OHOS_SM_HLOG("MaybeStartPlayback enter vq=%{public}d aq=%{public}d",
               (int)mVideoQueue.GetSize(), (int)mAudioQueue.GetSize());''')

io.open(p, 'w', encoding='utf-8').write(s)
print('state machine logs added')
