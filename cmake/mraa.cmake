# Copyright 2015 Samsung Electronics Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cmake_minimum_required(VERSION 2.8)

set(MRAA_ROOT ${DEP_ROOT}/mraa)
set(MRAA_INCDIR ${MRAA_ROOT}/api)
set(MRAA_LIB ${LIB_ROOT}/libmraa.so)

add_custom_command(OUTPUT ${MRAA_LIB}
                   COMMAND touch ${MRAA_LIB})

add_custom_target(targetMraa DEPENDS ${MRAA_LIB})
