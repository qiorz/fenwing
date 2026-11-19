/**
 * GeckoSurface - XComponent(SURFACE) host for the Gecko render target.
 *
 * M3 scope: real surface hand-off to libgeckoxcomp.so, touch/mouse/key
 * forwarding into the Gecko surface coordinate space, and a hidden TextInput
 * used as the IME bridge (the port does not use an OHOS IME NDK, it asks the
 * ArkTS layer to focus a TextInput and forwards text through insertText).
 *
 * Coordinate spaces:
 *  - ArkUI touch/mouse events are in vp, relative to this component;
 *  - Gecko expects pixels of the XComponent surface (see getSurfaceSize());
 *  - scale = surfacePixelSize / componentVpSize, computed per event.
 */

import { display } from '@kit.ArkUI';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { KeyCode } from '@kit.InputKit';
import { GeckoViewBoot, SurfaceSizeReport } from 'gecko';
import { SurfaceMetrics } from '../common/GeckoTypes';

const DOMAIN: number = 0x3202;
const TAG: string = 'GeckoSurface';

@Component
export struct GeckoSurface {
  /** Engine session this surface belongs to. Empty until M2 sessions exist. */
  @Prop sessionId: string = '';
  /** Draw the placeholder panel on top of the (empty) native surface. */
  @Prop showPlaceholder: boolean = true;

  @State private surfaceId: string = '';
  @State private statusText: string = 'Native surface not created';
  @State private compWidth: number = 0;
  @State private compHeight: number = 0;
  @State private imeText: string = '';
  private lastImeText: string = '';
  @StorageProp('geckoImeState') @Watch('onImeStateChanged') imeState: string = '';
  private controller: XComponentController = new XComponentController();

  /** Notifies the parent that a native surface is ready for attachSurface. */
  onSurfaceReady: (metrics: SurfaceMetrics) => void = () => {
  };
  /** Notifies the parent that the surface is gone and must be detached. */
  onSurfaceLost: (surfaceId: string) => void = () => {
  };

  aboutToAppear(): void {
    if (this.imeState.length > 0) {
      this.onImeStateChanged();
    }
  }

  /** Gecko asks ArkTS to show/hide the soft keyboard via AppStorage. */
  onImeStateChanged(): void {
    hilog.info(DOMAIN, TAG, 'IME state=%{public}s', this.imeState);
    if (this.imeState === 'show') {
      this.focusIme();
    } else {
      this.lastImeText = '';
      this.imeText = '';
      this.blurIme();
    }
  }

  aboutToDisappear(): void {
    if (this.surfaceId.length > 0) {
      this.onSurfaceLost(this.surfaceId);
    }
  }

  private focusIme(): void {
    try {
      this.getUIContext().getFocusController().requestFocus('gecko-ime');
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'requestFocus failed: %{public}s', JSON.stringify(error));
    }
  }

  private blurIme(): void {
    try {
      this.getUIContext().getFocusController().clearFocus();
    } catch (error) {
      hilog.warn(DOMAIN, TAG, 'clearFocus failed: %{public}s', JSON.stringify(error));
    }
  }

  /** vp -> surface pixel scale; 1:1 fallback until the engine reports a size. */
  private scaleX(): number {
    const size: SurfaceSizeReport = GeckoViewBoot.surfaceSize();
    if (size.width > 0 && this.compWidth > 0) {
      return size.width / this.compWidth;
    }
    return display.getDefaultDisplaySync().densityPixels;
  }

  private scaleY(): number {
    const size: SurfaceSizeReport = GeckoViewBoot.surfaceSize();
    if (size.height > 0 && this.compHeight > 0) {
      return size.height / this.compHeight;
    }
    return display.getDefaultDisplaySync().densityPixels;
  }

  private handleTouch(event: TouchEvent): void {
    if (event.touches.length === 0) {
      return;
    }
    let action: number = 2; // move
    if (event.type === TouchType.Down) {
      action = 0;
    } else if (event.type === TouchType.Up) {
      action = 1;
    } else if (event.type === TouchType.Cancel) {
      action = 3;
    }
    const touch = event.touches[0];
    GeckoViewBoot.touch(action, touch.x * this.scaleX(), touch.y * this.scaleY(), Date.now());
  }

  private handleMouse(event: MouseEvent): void {
    const x: number = event.x * this.scaleX();
    const y: number = event.y * this.scaleY();
    if (event.action === MouseAction.Move) {
      GeckoViewBoot.mouseMove(x, y);
    } else if (event.action === MouseAction.Press) {
      GeckoViewBoot.mouseDown(x, y, this.mapButton(event.button));
    } else if (event.action === MouseAction.Release) {
      GeckoViewBoot.mouseUp(x, y, this.mapButton(event.button));
    }
  }

  /** ArkUI MouseButton -> OHOS mouse button (0=left,1=middle,2=right). */
  private mapButton(button: MouseButton): number {
    if (button === MouseButton.Right) {
      return 2;
    }
    if (button === MouseButton.Middle) {
      return 1;
    }
    return 0;
  }

  private handleKey(event: KeyEvent): boolean {
    if (event.type !== KeyType.Down && event.type !== KeyType.Up) {
      return false;
    }
    // OHOS key action: 0=down, 1=up.
    const action: number = event.type === KeyType.Down ? 0 : 1;
    if (event.keyCode === KeyCode.KEYCODE_DEL || event.keyCode === KeyCode.KEYCODE_FORWARD_DEL) {
      if (event.type === KeyType.Down) {
        GeckoViewBoot.deleteText(1);
      }
      return true;
    }
    GeckoViewBoot.key(action, event.keyCode, 0);
    return true;
  }

  private handleSurfaceCreated(): void {
    try {
      const createdId: string = this.controller.getXComponentSurfaceId();
      this.surfaceId = createdId;
      this.statusText = `Surface ready: ${createdId}`;

      const metrics = new SurfaceMetrics();
      metrics.surfaceId = createdId;
      const rect: SurfaceRect = this.controller.getXComponentSurfaceRect();
      metrics.width = rect.surfaceWidth;
      metrics.height = rect.surfaceHeight;
      metrics.density = display.getDefaultDisplaySync().densityPixels;

      hilog.info(DOMAIN, TAG, 'Surface created id=%{public}s %{public}dx%{public}d',
        createdId, metrics.width, metrics.height);
      this.onSurfaceReady(metrics);
    } catch (error) {
      this.statusText = 'Surface created but metrics are unavailable';
      hilog.error(DOMAIN, TAG, 'Failed to read surface metrics: %{public}s', JSON.stringify(error));
    }
  }

  private handleSurfaceDestroyed(): void {
    const previousId: string = this.surfaceId;
    this.surfaceId = '';
    this.statusText = 'Native surface destroyed';
    hilog.info(DOMAIN, TAG, 'Surface destroyed id=%{public}s', previousId);
    if (previousId.length > 0) {
      this.onSurfaceLost(previousId);
    }
  }

  build() {
    Stack({ alignContent: Alignment.Center }) {
      XComponent({ id: 'gecko-surface', type: XComponentType.SURFACE, controller: this.controller, libraryname: 'geckoxcomp' })
        .width('100%')
        .height('100%')
        .onLoad(() => {
          this.handleSurfaceCreated();
        })
        .onDestroy(() => {
          this.handleSurfaceDestroyed();
        })
        .onAreaChange((oldArea: Area, newArea: Area) => {
          this.compWidth = Number(newArea.width);
          this.compHeight = Number(newArea.height);
        })
        .onTouch((event: TouchEvent) => {
          this.handleTouch(event);
        })
        .onMouse((event: MouseEvent) => {
          this.handleMouse(event);
        })
        .onAxisEvent((event: AxisEvent) => {
          const dx: number = event.axisHorizontal ?? 0;
          const dy: number = event.axisVertical ?? 0;
          if (Math.abs(dx) > 0.001 || Math.abs(dy) > 0.001) {
            GeckoViewBoot.scroll(dx, dy, event.x * this.scaleX(), event.y * this.scaleY());
          }
        })
        .onKeyEvent((event: KeyEvent) => {
          return this.handleKey(event);
        })

      // Hidden IME bridge: Gecko focuses this TextInput via the IME callback.
      // Only the DELTA between the previous and new value is forwarded, so the
      // page input never receives duplicated characters.
      TextInput({ text: this.imeText, placeholder: '' })
        .id('gecko-ime')
        .width(1)
        .height(1)
        .opacity(0.01)
        .enableKeyboardOnFocus(true)
        .caretColor(Color.Transparent)
        .onChange((value: string) => {
          const previous: string = this.lastImeText;
          if (value.startsWith(previous)) {
            const added: string = value.substring(previous.length);
            if (added.length > 0) {
              GeckoViewBoot.insertText(added);
            }
          } else if (previous.startsWith(value)) {
            GeckoViewBoot.deleteText(previous.length - value.length);
          } else {
            if (previous.length > 0) {
              GeckoViewBoot.deleteText(previous.length);
            }
            if (value.length > 0) {
              GeckoViewBoot.insertText(value);
            }
          }
          this.lastImeText = value;
          this.imeText = value;
        })

      if (this.showPlaceholder) {
        Column({ space: 8 }) {
          Text('Gecko render surface')
            .fontSize(18)
            .fontWeight(FontWeight.Medium)
            .fontColor('#E6E6F0')
          Text('XComponent(SURFACE) is live; content rendering is gated behind M3.')
            .fontSize(13)
            .fontColor('#A0A0B8')
            .textAlign(TextAlign.Center)
            .maxLines(2)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
          Text(this.statusText)
            .fontSize(11)
            .fontColor('#7C7C96')
            .maxLines(2)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
          Text(`session=${this.sessionId.length > 0 ? this.sessionId : 'none'}`)
            .fontSize(11)
            .fontColor('#7C7C96')
        }
        .padding(24)
        .alignItems(HorizontalAlign.Center)
        .justifyContent(FlexAlign.Center)
        .width('100%')
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#101014')
  }
}
