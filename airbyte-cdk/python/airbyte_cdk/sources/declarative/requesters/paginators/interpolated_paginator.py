#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.requesters.paginators.paginator import Paginator


class InterpolatedPaginator(Paginator):
    def __init__(self, next_page_token_template: Mapping[str, str], decoder: Decoder, config):
        self._next_page_token_template = InterpolatedMapping(next_page_token_template, JinjaInterpolation())
        self._decoder = decoder
        self._config = config

    def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
        decoded_response = self._decoder.decode(response)
        headers = response.headers
        interpolated_values = self._next_page_token_template.eval(
            self._config, decoded_response=decoded_response, headers=headers, last_records=last_records
        )

        non_null_tokens = {k: v for k, v in interpolated_values.items() if v}

        return non_null_tokens if non_null_tokens else None
