/**
 * SettingsView - browser settings, local account and diagnostics entry.
 *
 * The view is fully controlled: it never mutates persisted state itself, it
 * reports intent through callbacks so BrowserPage/SettingsRepository stay the
 * single source of truth.
 */

@Component
export struct SettingsView {
  @Prop javascriptEnabled: boolean = true;
  @Prop imagesEnabled: boolean = true;
  @Prop doNotTrack: boolean = true;
  @Prop privateByDefault: boolean = false;
  @Prop searchEngine: string = 'DuckDuckGo';
  @Prop accountName: string = '';
  @Prop engineLabel: string = '';
  @Prop uaMode: string = 'standard';

  onToggleJavascript: (enabled: boolean) => void = () => {
  };
  onToggleImages: (enabled: boolean) => void = () => {
  };
  onToggleDoNotTrack: (enabled: boolean) => void = () => {
  };
  onTogglePrivateByDefault: (enabled: boolean) => void = () => {
  };
  onChangeSearchEngine: (value: string) => void = () => {
  };
  onExportData: () => void = () => {
  };
  onImportData: () => void = () => {
  };
  onOpenDiagnostics: () => void = () => {
  };
  onUaModeChange: (mode: string) => void = () => {
  };

  @State private engineDraft: string = '';

  aboutToAppear(): void {
    this.engineDraft = this.searchEngine;
  }

  private handleToggle(kind: string, isOn: boolean): void {
    if (kind === 'javascript') {
      this.onToggleJavascript(isOn);
    } else if (kind === 'images') {
      this.onToggleImages(isOn);
    } else if (kind === 'dnt') {
      this.onToggleDoNotTrack(isOn);
    } else if (kind === 'private') {
      this.onTogglePrivateByDefault(isOn);
    }
  }

  @Builder
  toggleRow(title: string, description: string, checked: boolean, kind: string) {
    Row({ space: 10 }) {
      Column({ space: 2 }) {
        Text(title)
          .fontSize(14)
          .fontColor('#E6E6F0')
        Text(description)
          .fontSize(11)
          .fontColor('#7C7C96')
      }
      .alignItems(HorizontalAlign.Start)
      .layoutWeight(1)

      Toggle({ type: ToggleType.Switch, isOn: checked })
        .selectedColor('#4C6FFF')
        .onChange((isOn: boolean) => {
          this.handleToggle(kind, isOn);
        })
    }
    .width('100%')
    .padding({ top: 8, bottom: 8 })
  }

  @Builder
  uaButton(label: string, mode: string) {
    Button(label)
      .fontSize(12)
      .height(32)
      .layoutWeight(1)
      .backgroundColor(this.uaMode === mode ? '#3A5A9A' : '#17171F')
      .fontColor(this.uaMode === mode ? '#FFFFFF' : '#A0A0B8')
      .borderRadius(6)
      .onClick(() => {
        this.onUaModeChange(mode);
      })
  }

  build() {
    Scroll() {
      Column({ space: 10 }) {
        Text('设置')
          .fontSize(16)
          .fontWeight(FontWeight.Medium)
          .fontColor('#E6E6F0')
          .width('100%')

        Text('内容')
          .fontSize(12)
          .fontColor('#8A8AA3')
          .width('100%')
        this.toggleRow('启用 JavaScript', '关闭后仅显示静态内容', this.javascriptEnabled, 'javascript')
        this.toggleRow('加载图片', '关闭后节省流量', this.imagesEnabled, 'images')

        Text('隐私')
          .fontSize(12)
          .fontColor('#8A8AA3')
          .width('100%')
          .margin({ top: 6 })
        this.toggleRow('发送 Do Not Track', '请求站点不要跟踪', this.doNotTrack, 'dnt')
        this.toggleRow('默认隐私模式', '新标签不写历史与记录', this.privateByDefault, 'private')

        Text('兼容性（浏览器标识）')
          .fontSize(12)
          .fontColor('#8A8AA3')
          .width('100%')
          .margin({ top: 6 })
        Row({ space: 8 }) {
          this.uaButton('标准（Gecko）', 'standard')
          this.uaButton('手机', 'mobile')
        }
        .width('100%')
        Row({ space: 8 }) {
          this.uaButton('桌面', 'desktop')
          this.uaButton('Chrome 兼容', 'chrome')
        }
        .width('100%')
        Text('部分网站会按 UA 判断设备；遇到排版/功能异常可切换。')
          .fontSize(11)
          .fontColor('#7C7C96')
          .width('100%')

        Text('搜索')
          .fontSize(12)
          .fontColor('#8A8AA3')
          .width('100%')
          .margin({ top: 6 })
        Row({ space: 8 }) {
          TextInput({ text: this.engineDraft, placeholder: '搜索引擎名称' })
            .fontSize(13)
            .height(38)
            .backgroundColor('#1C1C26')
            .fontColor('#E6E6F0')
            .layoutWeight(1)
            .onChange((value: string) => {
              this.engineDraft = value;
            })
          Button('保存')
            .fontSize(13)
            .height(38)
            .backgroundColor('#243043')
            .fontColor('#CFE0FF')
            .onClick(() => {
              this.onChangeSearchEngine(this.engineDraft);
            })
        }
        .width('100%')

        Text('本地账户')
          .fontSize(12)
          .fontColor('#8A8AA3')
          .width('100%')
          .margin({ top: 6 })
        Row({ space: 8 }) {
          Text(this.accountName.length > 0 ? `已登录：${this.accountName}` : '未创建本地账户')
            .fontSize(13)
            .fontColor('#C9C9DE')
            .layoutWeight(1)
          Button('导出')
            .fontSize(12)
            .height(32)
            .backgroundColor('#1C1C26')
            .fontColor('#C9C9DE')
            .onClick(() => {
              this.onExportData();
            })
          Button('导入')
            .fontSize(12)
            .height(32)
            .backgroundColor('#1C1C26')
            .fontColor('#C9C9DE')
            .onClick(() => {
              this.onImportData();
            })
        }
        .width('100%')

        Text('引擎')
          .fontSize(12)
          .fontColor('#8A8AA3')
          .width('100%')
          .margin({ top: 6 })
        Column({ space: 4 }) {
          Text(this.engineLabel.length > 0 ? this.engineLabel : '原生桥未初始化')
            .fontSize(12)
            .fontColor('#C9C9DE')
            .width('100%')
          Text('Gecko 嵌入层按里程碑推进：M2 headless、M3 渲染、M4 网络。')
            .fontSize(11)
            .fontColor('#7C7C96')
            .width('100%')
        }
        .width('100%')
        .padding(10)
        .backgroundColor('#15151F')
        .borderRadius(8)

        Button('打开 M0 诊断页')
          .fontSize(13)
          .width('100%')
          .height(40)
          .margin({ top: 8 })
          .backgroundColor('#1C1C26')
          .fontColor('#CFE0FF')
          .onClick(() => {
            this.onOpenDiagnostics();
          })
      }
      .width('100%')
      .padding(12)
      .alignItems(HorizontalAlign.Start)
    }
    .width('100%')
    .height('100%')
  }
}
