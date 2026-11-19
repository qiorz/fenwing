/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#include "OHOSDecoderModule.h"

#include "OHOSVideoDecoder.h"
#include "VideoUtils.h"
#include "mozilla/StaticPrefs_media.h"

namespace mozilla {

already_AddRefed<PlatformDecoderModule> OHOSDecoderModule::Create() {
  return MakeAndAddRef<OHOSDecoderModule>();
}

media::DecodeSupportSet OHOSDecoderModule::SupportsMimeType(
    const nsACString& aMimeType, DecoderDoctorDiagnostics*) const {
  if (aMimeType.EqualsLiteral("video/avc") ||
      aMimeType.EqualsLiteral("video/hevc")) {
    return media::DecodeSupportSet{media::DecodeSupport::HardwareDecode};
  }
  return media::DecodeSupportSet{};
}

already_AddRefed<MediaDataDecoder> OHOSDecoderModule::CreateVideoDecoder(
    const CreateDecoderParams& aParams) {
  const TrackInfo& info = aParams.mConfig;
  if (!info.GetAsVideoInfo()) {
    return nullptr;
  }
  const nsACString& mime = info.mMimeType;
  if (!mime.EqualsLiteral("video/avc") && !mime.EqualsLiteral("video/hevc")) {
    return nullptr;
  }
  RefPtr<MediaDataDecoder> decoder =
      MakeAndAddRef<OHOSVideoDecoder>(aParams, mime);
  return decoder.forget();
}

}  // namespace mozilla
