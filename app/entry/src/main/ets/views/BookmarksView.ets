/**
 * BookmarksView - list, open and delete bookmarks for the active profile.
 */

import { Bookmark } from '../model/BrowserModels';

@Component
export struct BookmarksView {
  @Prop bookmarks: Array<Bookmark> = [];
  @Prop privateMode: boolean = false;

  onOpen: (url: string) => void = () => {
  };
  onRemove: (id: string) => void = () => {
  };
  onRefresh: () => void = () => {
  };

  build() {
    Column({ space: 8 }) {
      Row() {
        Text('书签')
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
        Text('隐私模式下不展示书签数据')
          .fontSize(12)
          .fontColor('#C9A7FF')
          .width('100%')
      } else if (this.bookmarks.length === 0) {
        Text('暂无书签。打开页面后点击“收藏”即可添加。')
          .fontSize(13)
          .fontColor('#8A8AA3')
          .width('100%')
      } else {
        List({ space: 6 }) {
          ForEach(this.bookmarks, (item: Bookmark) => {
            ListItem() {
              Row({ space: 8 }) {
                Column({ space: 2 }) {
                  Text(item.title.length > 0 ? item.title : item.url)
                    .fontSize(14)
                    .fontColor('#E6E6F0')
                    .maxLines(1)
                    .textOverflow({ overflow: TextOverflow.Ellipsis })
                    .width('100%')
                  Text(item.url)
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
                Button('删除')
                  .fontSize(12)
                  .height(30)
                  .backgroundColor('#2A1A1F')
                  .fontColor('#E6A3A3')
                  .onClick(() => {
                    this.onRemove(item.id);
                  })
              }
              .width('100%')
              .padding(10)
              .backgroundColor('#15151F')
              .borderRadius(8)
            }
          }, (item: Bookmark) => item.id)
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
