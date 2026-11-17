/**
 * DownloadsView - download records for the active profile.
 *
 * The engine download pipeline is M4/M5 work; this view renders records that
 * the shell creates and lets the user cancel/retry their local state.
 */

import { DownloadRecord, DownloadState } from '../model/BrowserModels';

@Component
export struct DownloadsView {
  @Prop records: Array<DownloadRecord> = [];
  @Prop privateMode: boolean = false;

  onCancel: (id: string) => void = () => {
  };
  onRetry: (id: string) => void = () => {
  };
  onRefresh: () => void = () => {
  };

  private percentOf(record: DownloadRecord): number {
    if (record.totalBytes <= 0) {
      return 0;
    }
    const percent = Math.round((record.receivedBytes * 100) / record.totalBytes);
    if (percent < 0) {
      return 0;
    }
    if (percent > 100) {
      return 100;
    }
    return percent;
  }

  private stateLabel(state: DownloadState): string {
    if (state === DownloadState.QUEUED) {
      return '排队中';
    }
    if (state === DownloadState.DOWNLOADING) {
      return '下载中';
    }
    if (state === DownloadState.PAUSED) {
      return '已暂停';
    }
    if (state === DownloadState.COMPLETED) {
      return '已完成';
    }
    if (state === DownloadState.FAILED) {
      return '失败';
    }
    return '已取消';
  }

  build() {
    Column({ space: 8 }) {
      Row() {
        Text('下载')
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
      }
      .width('100%')

      if (this.privateMode) {
        Text('隐私模式不会保留下载记录。')
          .fontSize(13)
          .fontColor('#C9A7FF')
          .width('100%')
      } else if (this.records.length === 0) {
        Text('暂无下载。')
          .fontSize(13)
          .fontColor('#8A8AA3')
          .width('100%')
      } else {
        List({ space: 6 }) {
          ForEach(this.records, (record: DownloadRecord) => {
            ListItem() {
              Column({ space: 6 }) {
                Row() {
                  Text(record.fileName.length > 0 ? record.fileName : record.url)
                    .fontSize(14)
                    .fontColor('#E6E6F0')
                    .maxLines(1)
                    .textOverflow({ overflow: TextOverflow.Ellipsis })
                    .layoutWeight(1)
                  Text(this.stateLabel(record.state))
                    .fontSize(12)
                    .fontColor(record.state === DownloadState.FAILED ? '#E6A3A3' : '#8A8AA3')
                }
                .width('100%')

                Progress({ value: this.percentOf(record), total: 100, type: ProgressType.Linear })
                  .width('100%')

                Row({ space: 6 }) {
                  Text(`${this.percentOf(record)}% · ${record.receivedBytes}/${record.totalBytes}`)
                    .fontSize(12)
                    .fontColor('#7C7C96')
                  Blank()
                  if (record.state === DownloadState.FAILED) {
                    Button('重试')
                      .fontSize(12)
                      .height(28)
                      .backgroundColor('#243043')
                      .fontColor('#CFE0FF')
                      .onClick(() => {
                        this.onRetry(record.id);
                      })
                  }
                  if (record.state === DownloadState.DOWNLOADING || record.state === DownloadState.QUEUED) {
                    Button('取消')
                      .fontSize(12)
                      .height(28)
                      .backgroundColor('#2A1A1F')
                      .fontColor('#E6A3A3')
                      .onClick(() => {
                        this.onCancel(record.id);
                      })
                  }
                }
                .width('100%')
              }
              .width('100%')
              .padding(10)
              .backgroundColor('#15151F')
              .borderRadius(8)
            }
          }, (record: DownloadRecord) => record.id)
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
