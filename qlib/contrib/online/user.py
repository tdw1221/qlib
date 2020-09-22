# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import logging

from ...log import get_module_logger
from ..evaluate import risk_analysis
from ...data import D


class User:
    def __init__(self, account, strategy, model, verbose=False):
        """
        A user in online system, which contains account, strategy and model three module.
            Parameter
                account : Account()
                strategy :
                    a strategy instance
                model :
                    a model instance
                report_save_path : string
                    the path to save report. Will not save report if None
                verbose : bool
                    Whether to print the info during the process
        """
        self.logger = get_module_logger("User", level=logging.INFO)
        self.account = account
        self.strategy = strategy
        self.model = model
        self.verbose = verbose

    def init_state(self, date):
        """
        init state when each trading date begin
            Parameter
                date : pd.Timestamp
        """
        self.account.init_state(today=date)
        self.strategy.init_state(trade_date=date, model=self.model, account=self.account)
        return

    def get_latest_trading_date(self):
        """
        return the latest trading date for user {user_id}
            Parameter
                user_id : string
            :return
                date : string (e.g '2018-10-08')
        """
        if not self.account.last_trade_date:
            return None
        return str(self.account.last_trade_date.date())

    def showReport(self, benchmark="SH000905"):
        """
        show the newly report (mean, std, information_ratio, annual)
            Parameter
                benchmark : string
                    bench that to be compared, 'SH000905' for csi500
        """
        bench = D.features([benchmark], ["$change"], disk_cache=True).loc[benchmark, "$change"]
        report = self.account.report.generate_report_dataframe()
        report["bench"] = bench
        analysis_result = {"pred": {}, "sub_bench": {}, "sub_cost": {}}
        r = (report["return"] - report["bench"]).dropna()
        analysis_result["sub_bench"][0] = risk_analysis(r)
        r = (report["return"] - report["bench"] - report["cost"]).dropna()
        analysis_result["sub_cost"][0] = risk_analysis(r)
        self.logger.info("Result of porfolio:")
        self.logger.info("sub_bench:")
        self.logger.info(analysis_result["sub_bench"][0])
        self.logger.info("sub_cost:")
        self.logger.info(analysis_result["sub_cost"][0])
        return report