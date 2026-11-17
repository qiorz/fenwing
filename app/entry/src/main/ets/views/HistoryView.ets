/**
 * HistoryView - recent visits for the active profile, with clear action.
 */

import { HistoryEntry } from '../model/BrowserModels';

@Component
export struct HistoryView {
  @Prop entries: Array<HistoryEntry> = [];
  @Prop privateMode: boolean = false;

  onOpen: (url: string) => void = () => {
  };
  onClear: () => void = () => {
  };
  onRefresh: () => void = () => {
  };

  private formatTime(timestamp: number): string {
    const date = new Date(timestamp);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hour = date.getHours();
    const minute = date.getMinutes();
    const paddedMinute = minute < 10 ? `0${minute}` : `${minute}`;
    return `${month}/${day} ${hour}:${paddedMinute}`;
  }

  build() {
    Column({ space: 8 }) {
      Row() {
        Text('历史')
          .fontSize(16)
          .fontWeight(FontWeight.Medium)
          .fontColor('#E6E6F0')
        Blank()
        Button('刷新')
          .fontSize(12)
          .height(30)
          .backgroundColor('#1C1C26')
          .fontColor('#C9C9DE')
          .onClick(() => {
            this.onRefresh();
          })
        Button('清空')
          .fontSize(12)
          .height(30)
          .margin({ left: 6 })
          .backgroundColor('#2A1A1F')
          .fontColor('#E6A3A3')
          .onClick(() => {
            this.onClear();
          })
      }
      .width('100%')

      if (this.privateMode) {
        Text('隐私模式不记录历史；切换到普通模式后再查看。')
          .fontSize(13)
          .fontColor('#C9A7FF')
          .width('100%')
      } else if (this.entries.length === 0) {
        Text('暂无历史记录。')
          .fontSize(13)
          .fontColor('#8A8AA3')
          .width('100%')
      } else {
        List({ space: 6 }) {
          ForEach(this.entries, (item: HistoryEntry) => {
            ListItem() {
              Row({ space: 8 }) {
                Column({ space: 2 }) {
                  Text(item.title.length > 0 ? item.title : item.url)
                    .fontSize(14)
                    .fontColor('#E6E6F0')
                    .maxLines(1)
                    .textOverflow({ overflow: TextOverflow.Ellipsis })
                    .width('100%')
                  Text(`${this.formatTime(item.visitedAt)} · ${item.url}`)
                    .fontSize(12)
                    .fontColor('#7C7C96')
                    .maxLines(1)
                    .textOverflow({ overflow: TextOverflow.Ellipsis })
                    .width('100%')
                }
                .alignItems(HorizontalAlign.Start)
                .layoutWeight(1)

                Button('打开')
                  .fontSize(12)
                  .height(30)
                  .backgroundColor('#243043')
                  .fontColor('#CFE0FF')
                  .onClick(() => {
                    this.onOpen(item.url);
                  })
              }
              .width('100%')
              .padding(10)
              .backgroundColor('#15151F')
              .borderRadius(8)
            }
          }, (item: HistoryEntry) => item.id)
        }
        .width('100%')
        .layoutWeight(1)
      }
    }
    .width('100%')
    .height('100%')
    .padding(12)
    .alignItems(HorizontalAlign.Start)
  }
}
