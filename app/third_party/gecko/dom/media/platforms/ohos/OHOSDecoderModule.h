/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#ifndef DOM_MEDIA_PLATFORMS_OHOS_OHOSDECODERMODULE_H_
#define DOM_MEDIA_PLATFORMS_OHOS_OHOSDECODERMODULE_H_

#include "PlatformDecoderModule.h"

namespace mozilla {

// Phase 1 hardware decoder: OpenHarmony OH_AVCodec video decoder (H.264/HEVC)
// producing NV12 frames as PlanarYCbCrImage.
class OHOSDecoderModule : public PlatformDecoderModule {
 public:
  OHOSDecoderModule() = default;

  static already_AddRefed<PlatformDecoderModule> Create();

  media::DecodeSupportSet SupportsMimeType(
      const nsACString& aMimeType,
      DecoderDoctorDiagnostics* aDiagnostics) const override;

  already_AddRefed<MediaDataDecoder> CreateVideoDecoder(
      const CreateDecoderParams& aParams) override;

  already_AddRefed<MediaDataDecoder> CreateAudioDecoder(
      const CreateDecoderParams& aParams) override {
    return nullptr;
  }

 private:
  ~OHOSDecoderModule() = default;
};

}  // namespace mozilla

#endif
