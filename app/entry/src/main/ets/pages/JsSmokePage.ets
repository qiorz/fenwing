/**
 * M1 JS smoke page: sends a script to evaluateScript and shows either the
 * result or the precise reason it is unavailable.
 *
 * The page is intentionally honest: when libmozjs.so is not staged the call
 * rejects with UNSUPPORTED and the UI explains the blocker instead of
 * pretending the engine works.
 */

import { hilog } from '@kit.PerformanceAnalysisKit';
import { GeckoService } from '../service/GeckoService';
import { GeckoError } from '../common/GeckoErrors';
import { toGeckoError } from '../common/GeckoErrors';

const DOMAIN: number = 0x3203;
const TAG: string = 'JsSmokePage';

@Entry
@Component
struct JsSmokePage {
  @State private script: string = '1 + 41';
  @State private output: string = '';
  @State private errorText: string = '';
  @State private busy: boolean = false;
  @State private engineAvailable: boolean = false;
  @State private elapsedMs: number = 0;

  private service: GeckoService = GeckoService.getInstance();

  aboutToAppear(): void {
    this.engineAvailable = this.service.hasJsEngine();
    if (!this.engineAvailable) {
      this.errorText = 'libmozjs.so 未暂存：M1 构建被环境阻塞，详见 m1-report.md。';
    }
  }

  private async runScript(): Promise<void> {
    this.busy = true;
    this.output = '';
    this.errorText = '';
    const startedAt: number = Date.now();
    try {
      const value: string = await this.service.evaluate(this.script, 2000);
      this.output = value;
      hilog.info(DOMAIN, TAG, 'evaluate ok');
    } catch (error) {
      const geckoError: GeckoError = toGeckoError(error as Object);
      this.errorText = `${geckoError.code}: ${geckoError.message}`;
      if (geckoError.isUnsupported()) {
        this.errorText += '\n\n降级路径：NAPI 桥仍可用（见 M0 冒烟页），JS 求值待 G1。';
      }
      hilog.error(DOMAIN, TAG, 'evaluate failed: %{public}s', geckoError.detail);
    } finally {
      this.elapsedMs = Date.now() - startedAt;
      this.busy = false;
    }
  }

  build() {
    Column({ space: 12 }) {
      Text('M1 · JS 求值冒烟')
        .fontSize(22)
        .fontWeight(FontWeight.Bold)
        .fontColor('#F2F2FA')
        .width('100%')

      Row() {
        Text(this.engineAvailable ? 'libmozjs 可用' : 'libmozjs 不可用')
          .fontSize(13)
          .fontColor(this.engineAvailable ? '#7FE0A8' : '#E6A3A3')
      }
      .width('100%')
      .padding(10)
      .backgroundColor('#1A1A24')
      .borderRadius(8)

      Text('脚本')
        .fontSize(13)
        .fontColor('#8A8AA3')
        .width('100%')
      TextInput({ text: this.script, placeholder: '例如 1 + 41' })
        .fontSize(14)
        .height(44)
        .onChange((value: string) => {
          this.script = value;
        })

      Button(this.busy ? '执行中…' : '执行脚本')
        .fontSize(15)
        .width('100%')
        .height(44)
        .enabled(!this.busy)
        .onClick(() => {
          this.runScript();
        })

      if (this.output.length > 0) {
        Text('结果')
          .fontSize(13)
          .fontColor('#8A8AA3')
          .width('100%')
        Text(this.output)
          .fontSize(15)
          .fontColor('#E6E6F0')
          .width('100%')
          .padding(12)
          .backgroundColor('#15151F')
          .borderRadius(8)
      }

      if (this.errorText.length > 0) {
        Text('状态 / 错误')
          .fontSize(13)
          .fontColor('#8A8AA3')
          .width('100%')
        Text(this.errorText)
          .fontSize(13)
          .fontColor('#E6A3A3')
          .width('100%')
          .padding(12)
          .backgroundColor('#1F1518')
          .borderRadius(8)
      }

      Text(`耗时 ${this.elapsedMs} ms`)
        .fontSize(12)
        .fontColor('#7C7C96')
        .width('100%')
    }
    .width('100%')
    .height('100%')
    .padding(24)
    .alignItems(HorizontalAlign.Start)
    .backgroundColor('#0E0E12')
  }
}
