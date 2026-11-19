import io
p='/home/dev/ff/gecko/dom/media/platforms/ohos/OHOSDecoderModule.cpp'
lines=io.open(p,encoding='utf-8').read().split('\n')
print('\n'.join(f'{i+1}: {lines[i]}' for i in range(8,40)))
