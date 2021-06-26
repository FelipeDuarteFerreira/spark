#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import warnings
from typing import Any, Union

import pandas as pd
from pandas.api.types import CategoricalDtype

from pyspark.sql import functions as F
from pyspark.sql.types import BooleanType, DateType, StringType

from pyspark.pandas.base import column_op, IndexOpsMixin
from pyspark.pandas.data_type_ops.base import (
    DataTypeOps,
    IndexOpsLike,
    T_IndexOps,
    _as_bool_type,
    _as_categorical_type,
    _as_other_type,
    _as_string_type,
)
from pyspark.pandas.typedef import Dtype, pandas_on_spark_type


class DateOps(DataTypeOps):
    """
    The class for binary operations of pandas-on-Spark objects with spark type: DateType.
    """

    @property
    def pretty_name(self) -> str:
        return "dates"

    def sub(self, left: T_IndexOps, right: Any) -> IndexOpsLike:
        # Note that date subtraction casts arguments to integer. This is to mimic pandas's
        # behaviors. pandas returns 'timedelta64[ns]' in days from date's subtraction.
        msg = (
            "Note that there is a behavior difference of date subtraction. "
            "The date subtraction returns an integer in days, "
            "whereas pandas returns 'timedelta64[ns]'."
        )
        if isinstance(right, IndexOpsMixin) and isinstance(right.spark.data_type, DateType):
            warnings.warn(msg, UserWarning)
            return column_op(F.datediff)(left, right).astype("long")
        elif isinstance(right, datetime.date) and not isinstance(right, datetime.datetime):
            warnings.warn(msg, UserWarning)
            return column_op(F.datediff)(left, F.lit(right)).astype("long")
        else:
            raise TypeError("date subtraction can only be applied to date series.")

    def rsub(self, left: T_IndexOps, right: Any) -> IndexOpsLike:
        # Note that date subtraction casts arguments to integer. This is to mimic pandas's
        # behaviors. pandas returns 'timedelta64[ns]' in days from date's subtraction.
        msg = (
            "Note that there is a behavior difference of date subtraction. "
            "The date subtraction returns an integer in days, "
            "whereas pandas returns 'timedelta64[ns]'."
        )
        if isinstance(right, datetime.date) and not isinstance(right, datetime.datetime):
            warnings.warn(msg, UserWarning)
            return -column_op(F.datediff)(left, F.lit(right)).astype("long")
        else:
            raise TypeError("date subtraction can only be applied to date series.")

    def astype(self, index_ops: T_IndexOps, dtype: Union[str, type, Dtype]) -> T_IndexOps:
        dtype, spark_type = pandas_on_spark_type(dtype)

        if isinstance(dtype, CategoricalDtype):
            return _as_categorical_type(index_ops, dtype, spark_type)
        elif isinstance(spark_type, BooleanType):
            return _as_bool_type(index_ops, dtype)
        elif isinstance(spark_type, StringType):
            return _as_string_type(index_ops, dtype, null_str=str(pd.NaT))
        else:
            return _as_other_type(index_ops, dtype, spark_type)
