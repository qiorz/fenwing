/**
 * TabBar - horizontal tab strip with per-tab close buttons.
 *
 * Receives a plain TabChip array (primitive fields only) so V1 @Prop copies
 * cannot drop behaviour. All actions go back to BrowserPage / TabViewModel.
 */

import { TabChip } from '../model/BrowserModels';

@Component
export struct TabBar {
  @Prop tabs: Array<TabChip> = [];
  @Prop activeTabId: string = '';
  @Prop privateMode: boolean = false;

  onSelectTab: (tabId: string) => void = () => {
  };
  onCloseTab: (tabId: string) => void = () => {
  };
  onNewTab: () => void = () => {
  };

  private titleOf(chip: TabChip): string {
    if (chip.title.length > 0) {
      return chip.title;
    }
    if (chip.url.length > 0) {
      return chip.url;
    }
    return '新标签页';
  }

  build() {
    Row({ space: 8 }) {
      List({ space: 6 }) {
        ForEach(this.tabs, (chip: TabChip) => {
          ListItem() {
            Row({ space: 6 }) {
              Text(chip.privateMode ? '◍' : '●')
                .fontSize(9)
                .fontColor(chip.privateMode ? '#C9A7FF' : '#6E6E85')
              Text(this.titleOf(chip))
                .fontSize(12)
                .fontColor(chip.id === this.activeTabId ? '#F2F2FA' : '#A0A0B8')
                .maxLines(1)
                .textOverflow({ overflow: TextOverflow.Ellipsis })
                .layoutWeight(1)
              Text('✕')
                .fontSize(12)
                .fontColor('#8A8AA3')
                .padding({ left: 4, right: 4 })
                .onClick(() => {
                  this.onCloseTab(chip.id);
                })
            }
            .width(168)
            .padding({ left: 10, right: 8, top: 7, bottom: 7 })
            .backgroundColor(chip.id === this.activeTabId ? '#242433' : '#17171F')
            .borderRadius(8)
            .onClick(() => {
              this.onSelectTab(chip.id);
            })
          }
        }, (chip: TabChip) => `${chip.id}|${chip.title}|${chip.id === this.activeTabId}`)
      }
      .listDirection(Axis.Horizontal)
      .scrollBar(BarState.Off)
      .layoutWeight(1)
      .height(40)

      Button('+')
        .fontSize(18)
        .width(36)
        .height(36)
        .fontColor('#E6E6F0')
        .backgroundColor('#1C1C26')
        .borderRadius(8)
        .onClick(() => {
          this.onNewTab();
        })
    }
    .width('100%')
    .padding({ left: 12, right: 12, top: 6, bottom: 8 })
    .backgroundColor('#0E0E12')
  }
}
