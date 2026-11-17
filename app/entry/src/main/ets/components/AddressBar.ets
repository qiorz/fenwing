/**
 * AddressBar - URL input plus navigation controls.
 *
 * Stateless apart from the draft text: navigation intents are handed back to
 * BrowserPage, which owns the tab state.
 */

@Component
export struct AddressBar {
  @Prop @Watch('onUrlChanged') url: string = '';
  @Prop canGoBack: boolean = false;
  @Prop canGoForward: boolean = false;
  @Prop loading: boolean = false;
  @Prop privateMode: boolean = false;

  @State private draft: string = '';

  onNavigate: (input: string) => void = () => {
  };
  onBack: () => void = () => {
  };
  onForward: () => void = () => {
  };
  onReload: () => void = () => {
  };
  onStop: () => void = () => {
  };

  aboutToAppear(): void {
    this.draft = this.url;
  }

  onUrlChanged(): void {
    this.draft = this.url;
  }

  @Builder
  navButton(glyph: string, enabled: boolean, action: () => void) {
    Button(glyph)
      .fontSize(16)
      .fontColor(enabled ? '#E6E6F0' : '#4A4A5C')
      .backgroundColor('#1C1C26')
      .borderRadius(8)
      .width(36)
      .height(36)
      .enabled(enabled)
      .onClick(() => {
        action();
      })
  }

  build() {
    Row({ space: 6 }) {
      Button('←')
        .fontSize(16)
        .fontColor(this.canGoBack ? '#E6E6F0' : '#4A4A5C')
        .backgroundColor('#1C1C26')
        .borderRadius(8)
        .width(36)
        .height(36)
        .enabled(this.canGoBack)
        .onClick(() => {
          this.onBack();
        })
      Button('→')
        .fontSize(16)
        .fontColor(this.canGoForward ? '#E6E6F0' : '#4A4A5C')
        .backgroundColor('#1C1C26')
        .borderRadius(8)
        .width(36)
        .height(36)
        .enabled(this.canGoForward)
        .onClick(() => {
          this.onForward();
        })
      if (this.loading) {
        this.navButton('✕', true, () => {
          this.onStop();
        })
      } else {
        this.navButton('⟳', true, () => {
          this.onReload();
        })
      }

      TextInput({ text: this.draft, placeholder: '搜索或输入网址' })
        .fontSize(14)
        .fontColor('#E6E6F0')
        .placeholderColor('#6E6E85')
        .backgroundColor('#1C1C26')
        .borderRadius(8)
        .height(36)
        .layoutWeight(1)
        .enterKeyType(EnterKeyType.Go)
        .onChange((value: string) => {
          this.draft = value;
        })
        .onSubmit(() => {
          this.onNavigate(this.draft);
        })

      if (this.privateMode) {
        Text('私密')
          .fontSize(11)
          .fontColor('#C9A7FF')
          .padding({ left: 8, right: 8, top: 4, bottom: 4 })
          .backgroundColor('#2A1F3A')
          .borderRadius(6)
      }

      Button('前往')
        .fontSize(13)
        .height(36)
        .backgroundColor('#4C6FFF')
        .fontColor('#FFFFFF')
        .borderRadius(8)
        .onClick(() => {
          this.onNavigate(this.draft);
        })
    }
    .width('100%')
    .padding({ left: 12, right: 12, top: 8, bottom: 8 })
    .backgroundColor('#12121A')
  }
}
