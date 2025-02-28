/* -*- Mode: C++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 2 -*- */
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#include "RenderPipeline.h"

#include "Device.h"

namespace mozilla {
namespace webgpu {

GPU_IMPL_CYCLE_COLLECTION(RenderPipeline, mParent)
GPU_IMPL_JS_WRAP(RenderPipeline)

RenderPipeline::RenderPipeline(Device* const aParent, RawId aId,
                               nsTArray<RawId>&& aImplicitBindGroupLayoutIds)
    : ChildOf(aParent),
      mImplicitBindGroupLayoutIds(std::move(aImplicitBindGroupLayoutIds)),
      mId(aId) {}

RenderPipeline::~RenderPipeline() { Cleanup(); }

void RenderPipeline::Cleanup() {
  if (mValid && mParent) {
    mValid = false;
    auto bridge = mParent->GetBridge();
    if (bridge && bridge->IsOpen()) {
      bridge->SendRenderPipelineDestroy(mId);
    }
  }
}

already_AddRefed<BindGroupLayout> RenderPipeline::GetBindGroupLayout(
    uint32_t index) const {
  RefPtr<BindGroupLayout> object =
      new BindGroupLayout(mParent, mImplicitBindGroupLayoutIds[index]);
  return object.forget();
}

}  // namespace webgpu
}  // namespace mozilla
