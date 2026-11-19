import io
p='/home/dev/ff/gecko/dom/media/MediaFormatReader.cpp'
lines=io.open(p,encoding='utf-8',errors='replace').read().split('\n')
print('\n'.join(f'{i+1}: {lines[i]}' for i in range(2760,2840)))
