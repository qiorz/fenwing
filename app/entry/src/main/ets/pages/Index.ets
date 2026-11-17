/**
 * M0 debug page: proves the HAP -> HSP -> NAPI -> Rust chain and shows the
 * engine identity reported by the native bridge.
 *
 * This page intentionally does not render web content: the Gecko embedding
 * layer is gated behind M2/M3. Anything unavailable is displayed as such.
 */

import { router } from '@kit.ArkUI';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { GeckoService } from '../service/GeckoService';
import { EngineAvailability, EngineProbeResult, EngineVersionSummary } from '../common/GeckoTypes';

@Entry
@Component
struct Index {
  @State private version: EngineVersionSummary = new EngineVersionSummary();
  @State private probeResult: EngineProbeResult = new EngineProbeResult();
  @State private busy: boolean = false;
  @State private statusLine: string = '尚未运行冒烟测试';

  private service: GeckoService = GeckoService.getInstance();

  aboutToAppear(): void {
    this.version = this.service.getVersionSummary();
    this.runProbe();
  }

  private async runProbe(): Promise<void> {
    this.busy = true;
    this.statusLine = '正在执行 ArkTS → NAPI → Rust 冒烟…';
    const result: EngineProbeResult = await this.service.probe();
    this.probeResult = result;
    this.version = this.service.getVersionSummary();
    this.statusLine = result.ok ? 'PASS：M0 链路已验证' : 'FAIL：请查看错误列表';
    this.busy = false;
  }

  private goBack(): void {
    try {
      this.getUIContext().getRouter().back();
    } catch (error) {
      hilog.error(0x3201, 'IndexPage', 'back failed: %{public}s', JSON.stringify(error));
    }
  }

  private openJsSmoke(): void {
    const options: router.RouterOptions = { url: 'pages/JsSmokePage' };
    try {
      this.getUIContext().getRouter().pushUrl(options);
    } catch (error) {
      hilog.error(0x3201, 'IndexPage', 'Failed to open JsSmokePage: %{public}s', JSON.stringify(error));
    }
  }

  private availabilityLabel(): string {
    if (this.version.availability === EngineAvailability.BRIDGE_ONLY) {
      return '桥接可用（引擎未嵌入，M0）';
    }
    if (this.version.availability === EngineAvailability.JS_ONLY) {
      return 'JS 引擎可用（M1）';
    }
    if (this.version.availability === EngineAvailability.READY) {
      return '引擎可用';
    }
    if (this.version.availability === EngineAvailability.UNAVAILABLE) {
      return '原生模块不可用';
    }
    return '未知';
  }

  @Builder
  infoRow(label: string, value: string) {
    Row() {
      Text(label)
        .fontSize(13)
        .fontColor('#8A8AA3')
        .width(132)
      Text(value)
        .fontSize(13)
        .fontColor('#E6E6F0')
        .layoutWeight(1)
    }
    .width('100%')
    .alignItems(VerticalAlign.Top)
    .padding({ top: 5, bottom: 5 })
  }

  @Builder
  sectionTitle(title: string) {
    Text(title)
      .fontSize(15)
      .fontWeight(FontWeight.Medium)
      .fontColor('#C9C9DE')
      .margin({ top: 8, bottom: 4 })
  }

  build() {
    Scroll() {
      Column({ space: 4 }) {
        Row() {
          Text('Gecko for HarmonyOS')
            .fontSize(24)
            .fontWeight(FontWeight.Bold)
            .fontColor('#F2F2FA')
            .layoutWeight(1)
          Button('返回浏览器')
            .fontSize(12)
            .height(32)
            .backgroundColor('#1C1C26')
            .fontColor('#C9C9DE')
            .onClick(() => {
              this.goBack();
            })
        }
        .width('100%')
        Text('M0 冒烟：HAP + HSP + NAPI + Rust .so')
          .fontSize(13)
          .fontColor('#8A8AA3')
          .margin({ bottom: 8 })

        Row() {
          Text(this.statusLine)
            .fontSize(13)
            .fontColor(this.probeResult.ok ? '#7FE0A8' : '#E6A3A3')
            .layoutWeight(1)
          Button(this.busy ? '执行中…' : '重新测试')
            .fontSize(13)
            .height(34)
            .enabled(!this.busy)
            .onClick(() => {
              this.runProbe();
            })
        }
        .width('100%')
        .padding(12)
        .backgroundColor('#1A1A24')
        .borderRadius(10)

        this.sectionTitle('引擎版本（NAPI getVersion）')
        this.infoRow('engine', this.version.engine)
        this.infoRow('buildId', this.version.buildId)
        this.infoRow('Firefox 基线', this.version.geckoVersion)
        this.infoRow('ABI', this.version.abi)
        this.infoRow('JS 引擎', this.version.jsEngine)
        this.infoRow('Rust 桥', `${this.version.rustBridge} (abi=${this.version.rustBridgeAbi})`)
        this.infoRow('NAPI schema', `${this.version.napiSchemaVersion}`)
        this.infoRow('可用性', this.availabilityLabel())

        this.sectionTitle('冒烟结果')
        this.infoRow('ping', this.probeResult.pingReply.length > 0 ? this.probeResult.pingReply : '—')
        this.infoRow('Rust 加法',
          `${this.probeResult.rustAddLeft} + ${this.probeResult.rustAddRight} = ${this.probeResult.rustAddResult}`)
        this.infoRow('Rust 桥状态', this.probeResult.rustBridgeOk ? 'OK' : 'FAILED')
        this.infoRow('JS 求值', this.probeResult.jsEngineAvailable ? '可用' : '不可用（M1 阻塞）')
        this.infoRow('耗时', `${this.probeResult.elapsedMs()} ms`)

        if (this.probeResult.errors.length > 0) {
          this.sectionTitle('错误')
          ForEach(this.probeResult.errors, (item: string) => {
            Text(item)
              .fontSize(12)
              .fontColor('#E6A3A3')
              .width('100%')
              .padding({ top: 2, bottom: 2 })
          }, (item: string) => item)
        }

        Button('打开 JS 冒烟页')
          .fontSize(14)
          .width('100%')
          .height(42)
          .margin({ top: 16 })
          .onClick(() => {
            this.openJsSmoke();
          })
      }
      .width('100%')
      .padding(24)
      .alignItems(HorizontalAlign.Start)
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0E0E12')
  }
}
