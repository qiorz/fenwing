/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#ifndef DOM_MEDIA_PLATFORMS_OHOS_OHOSVIDEODECODER_H_
#define DOM_MEDIA_PLATFORMS_OHOS_OHOSVIDEODECODER_H_

#include <multimedia/player_framework/native_avcodec_base.h>
#include <multimedia/player_framework/native_avcodec_videodecoder.h>

#include "MediaData.h"
#include "PlatformDecoderModule.h"
#include "mozilla/Mutex.h"

namespace mozilla {

namespace layers {
class ImageContainer;
}  // namespace layers

class OHOSVideoDecoder final : public MediaDataDecoder {
 public:
  NS_INLINE_DECL_THREADSAFE_REFCOUNTING(OHOSVideoDecoder, override)
  OHOSVideoDecoder(const CreateDecoderParams& aParams, const nsACString& aMime);

  RefPtr<InitPromise> Init() override;
  RefPtr<DecodePromise> Decode(MediaRawData* aSample) override;
  RefPtr<DecodePromise> Drain() override;
  RefPtr<FlushPromise> Flush() override;
  RefPtr<ShutdownPromise> Shutdown() override;
  bool IsHardwareAccelerated(nsACString&) const override { return true; }
  nsCString GetCodecName() const override { return "ohos-hw"_ns; }
  ConversionRequired NeedsConversion() const override {
    return ConversionRequired::kNeedAnnexB;
  }
  nsCString GetDescriptionName() const override {
    return "OHOSVideoDecoder (OH_AVCodec HW)"_ns;
  }

 private:
  ~OHOSVideoDecoder() override = default;

  static void OnError(OH_AVCodec* aCodec, int32_t aErrorCode, void* aUserData);
  static void OnStreamChanged(OH_AVCodec* aCodec, OH_AVFormat* aFormat,
                              void* aUserData);
  static void OnNeedInputBuffer(OH_AVCodec* aCodec, uint32_t aIndex,
                                OH_AVBuffer* aBuffer, void* aUserData);
  static void OnNewOutputBuffer(OH_AVCodec* aCodec, uint32_t aIndex,
                                OH_AVBuffer* aBuffer, void* aUserData);

  void HandleOutput(uint32_t aIndex, OH_AVBuffer* aBuffer);

  const VideoInfo mInfo;
  const nsCString mMimeType;
  layers::ImageContainer* mImageContainer = nullptr;
  OH_AVCodec* mCodec = nullptr;
  gfx::IntSize mSize;
  bool mStarted = false;

  Mutex mMutex;
  RefPtr<MediaRawData> mPendingSample;
  nsTArray<RefPtr<MediaData>> mFrames;
  MozPromiseHolder<DecodePromise> mDecodePromise;
  bool mEOS = false;
  bool mShutdown = false;
};

}  // namespace mozilla

#endif
