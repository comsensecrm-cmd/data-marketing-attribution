import polars as pl


whatsapp_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\WA_OCT_NOV.csv", ignore_errors=True)
email_oct_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\OCT_Email.csv", ignore_errors=True)
sms_oct_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\SMS_Click.csv", ignore_errors=True)
sms_nov_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\SMS_NOV_Data_20251205.csv", ignore_errors=True)
email_nov_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\Nov_Email_report_Month_720251125.csv", ignore_errors=True)


invoice_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\LOB_data_1stOct_to30thNov (1)\Invoice_Data_Oct_Nov20251205.csv", ignore_errors=True)
service_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\LOB_data_1stOct_to30thNov (1)\Service_Data_Oct_Nov20251204.csv")
gma_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\LOB_data_1stOct_to30thNov (1)\GMA_Data_Oct_Nov20251205.csv")
softproduct_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\LOB_data_1stOct_to30thNov (1)\SoftProduct_Data_Oct_Nov20251205.csv")
cdpgear_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\LOB_data_1stOct_to30thNov (1)\cdpgear_Data_Oct_Nov20251205.csv")
magento_data = pl.scan_csv(r"D:\Backup data\RE\attribution_Oct_Nov\data\LOB_data_1stOct_to30thNov (1)\Magento_Data_Oct_Nov20251205.csv")


# Apply column transformations and standardize the required fields.
sms_nov_data = sms_nov_data.with_columns(
    (pl.col("Mobile").alias("MobileNumber")),
    (pl.col("Name").alias("CampaignName")))


# Apply column transformations and standardize the required fields.
email_nov_data = email_nov_data.with_columns(
    (pl.when(pl.col("SubscriberKey").cast(pl.String).str.starts_with("91"))
    .then(pl.col("SubscriberKey").cast(pl.String).str.slice(2))
    .otherwise(pl.col("SubscriberKey"))
    .cast(pl.Int64)
    .alias("SubscriberKey")),
    (pl.col("OpenEventDate").str.replace_all(r"\s+", " ")
    .str.strptime(pl.Datetime, "%b %d %Y %I:%M%p")
    .alias("OpenEventDate"))
)


# Apply column transformations and standardize the required fields.
email_oct_data = email_oct_data.with_columns(
    (pl.when(pl.col("SubscriberKey").cast(pl.String).str.starts_with("91"))
    .then(pl.col("SubscriberKey").cast(pl.String).str.slice(2))
    .otherwise(pl.col("SubscriberKey"))
    .cast(pl.Int64)
    .alias("SubscriberKey")),
    (pl.col("OpenEventDate").str.replace_all(r"\s+", " ")
    .str.strptime(pl.Datetime, "%b %d %Y %I:%M%p")
    .alias("OpenEventDate"))
)


# Apply column transformations and standardize the required fields.
sms_oct_data = sms_oct_data.with_columns(
    (pl.when(pl.col("MobileNumber").cast(pl.String).str.starts_with("91"))
    .then(pl.col("MobileNumber").cast(pl.String).str.slice(2))
    .otherwise(pl.col("MobileNumber"))
    .cast(pl.Int64)
    .alias("MobileNumber")),
    (pl.col("CreatedAt").str.strptime(pl.Date, format="%m/%d/%Y %I:%M:%S %p")
    .alias("CreatedAt"))
)


# Apply column transformations and standardize the required fields.
sms_nov_data = sms_nov_data.with_columns(
    (pl.when(pl.col("MobileNumber").cast(pl.String).str.starts_with("91"))
    .then(pl.col("MobileNumber").cast(pl.String).str.slice(2))
    .otherwise(pl.col("MobileNumber"))
    .cast(pl.Int64)
    .alias("MobileNumber")),
    (pl.col("ActionDateTime").str.strptime(pl.Date, format="%b %d %Y %I:%M%p")
    .alias("ActionDateTime"))
)


# Apply column transformations and standardize the required fields.
whatsapp_data = whatsapp_data.with_columns(
    (pl.when(pl.col("MobileNumber").cast(pl.String).str.starts_with("91"))
    .then(pl.col("MobileNumber").cast(pl.String).str.slice(2))
    .otherwise(pl.col("MobileNumber"))
    .cast(pl.Int64)
    .alias("MobileNumber")),
    (pl.col("EventDateUTC").str.strptime(pl.Date, format="%m/%d/%Y %I:%M:%S %p")
    .alias("EventDateUTC"))
)


# ##### ***INVOICE ATTRIBUTION***


# Apply column transformations and standardize the required fields.
invoice_data = invoice_data.with_columns(pl.col("sale_date").str.strptime(pl.Date, format="%Y-%m-%d").alias("sale_date"))


# Join the datasets using the required customer-level key.
email_invoice_oct_attribution = email_oct_data.join(invoice_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


# Join the datasets using the required customer-level key.
email_invoice_nov_attribution = email_nov_data.join(invoice_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


email_invoice_df = pl.concat([email_invoice_oct_attribution, email_invoice_nov_attribution]).unique(subset=["SubscriberKey", "JourneyName"])


# Join the datasets using the required customer-level key.
sms_invoice_oct_attribution  = sms_oct_data.join(invoice_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("CreatedAt") <= pl.col("sale_date")).unique(subset=["MobileNumber"]).select(["MobileNumber", "CampaignName"])


# Join the datasets using the required customer-level key.
sms_invoice_nov_attribution = sms_nov_data.join(invoice_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("ActionDateTime") <= pl.col("sale_date")).unique(subset=["MobileNumber"]).select(["MobileNumber", "CampaignName"])


sms_invoice_df = pl.concat([sms_invoice_oct_attribution, sms_invoice_nov_attribution]).unique(subset=["MobileNumber", "CampaignName"])


# Join the datasets using the required customer-level key.
whatsapp_invoice_df = whatsapp_data.join(invoice_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("EventDateUTC") <= pl.col("sale_date")).unique(subset=["MobileNumber"])


whatsapp_invoice_df = whatsapp_invoice_df.rename({"MobileNumber": "SubscriberKey"})
sms_invoice_df = sms_invoice_df.rename({"MobileNumber": "SubscriberKey"})


email_invoice_df.join(
        sms_invoice_df,
        on="SubscriberKey",
        how="inner"
    ).join(
        whatsapp_invoice_df,
        on="SubscriberKey",
        how="inner"
    ).unique(subset=["SubscriberKey", "CampaignName"]).collect().count()


# ##### ***SERVICE ATTRIBUTION***


# Apply column transformations and standardize the required fields.
service_data = service_data.with_columns(pl.col("sale_date").str.strptime(pl.Date, format="%Y-%m-%d").alias("sale_date"))


# whatsapp_data.join(service_data, left_on="MobileNumber",
# right_on="Mobile_Number",
# how="inner"
# ).filter(pl.col("EventDateUTC") <= pl.col("sale_date")).unique(subset=["MobileNumber"])


sms_oct_data.join(service_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("CreatedAt") <= pl.col("sale_date")).unique(subset=["MobileNumber"]).collect().count()


sms_nov_data.join(service_data, left_on="Mobile",
right_on="Mobile_Number",
how="inner"
).filter(
    (pl.col("ActionDateTime") <= pl.col("sale_date")) &
    (pl.col("Delivered") == 1)
).unique(subset=["Mobile"]).collect().count()


# Join the datasets using the required customer-level key.
email_service_oct_attrbiution = email_oct_data.join(service_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


# Join the datasets using the required customer-level key.
email_service_nov_attrbiution = email_nov_data.join(service_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


# pl.concat([email_service_oct_attrbiution, email_service_nov_attrbiution]).unique(subset=["SubscriberKey", "JourneyName"]).collect().count()


# #### ***GMA ATTRIBUTION***


# Apply column transformations and standardize the required fields.
gma_data = gma_data.with_columns(
    (pl.col("sale_date").str.strptime(pl.Date, format="%Y-%m-%d").alias("sale_date")))


# Join the datasets using the required customer-level key.
whatsapp_gma_data = whatsapp_data.join(gma_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("EventDateUTC") <= pl.col("sale_date")).unique(subset=["MobileNumber"])


# Join the datasets using the required customer-level key.
sms_gma_oct_attribution = sms_oct_data.join(gma_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("CreatedAt") <= pl.col("sale_date")).unique(subset=["MobileNumber", "CampaignName"]).select(["MobileNumber", "CampaignName"])


# Join the datasets using the required customer-level key.
sms_gma_nov_attribution = sms_nov_data.join(
    gma_data,
    left_on="MobileNumber",
    right_on="Mobile_Number",
    how="inner"
).filter(
    (pl.col("ActionDateTime") <= pl.col("sale_date")) &
    (pl.col("Delivered") == 1)
).select(pl.col("MobileNumber").n_unique()).select(["MobileNumber", "CampaignName"])


sms_gma_nov_attribution.collect().head(1)


pl.concat([sms_gma_oct_attribution, sms_gma_nov_attribution]).unique(subset=["MobileNumber", "CampaignName"]).collect().count()


# Join the datasets using the required customer-level key.
email_gma_oct_attribution = email_oct_data.join(gma_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


# Join the datasets using the required customer-level key.
email_gma_nov_attribution = email_nov_data.join(gma_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


pl.concat([email_gma_oct_attribution, email_gma_nov_attribution]).unique(subset=["SubscriberKey", "JourneyName"]).collect().count()


# ##### ***SOFT PRODUCT ATTRIBUTION***


softproduct_data.collect().head(1)


# Apply column transformations and standardize the required fields.
softproduct_data = softproduct_data.with_columns(pl.col("sale_date").str.strptime(pl.Date, format="%Y-%m-%d").alias("sale_date"))


whatsapp_data.join(softproduct_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("EventDateUTC") <= pl.col("sale_date")).unique(subset=["MobileNumber"]).collect().count()


# Join the datasets using the required customer-level key.
sms_soft_oct_attribution = sms_oct_data.join(softproduct_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("CreatedAt") <= pl.col("sale_date")).unique(subset=["MobileNumber", "CampaignName"]).select(["MobileNumber", "CampaignName"])


# Join the datasets using the required customer-level key.
sms_soft_nov_attribution =sms_nov_data.join(softproduct_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(
    (pl.col("ActionDateTime") <= pl.col("sale_date")) &
    (pl.col("Delivered") == 1)
).unique(subset=["MobileNumber"]).select(["MobileNumber", "CampaignName"])


pl.concat([sms_soft_oct_attribution, sms_soft_nov_attribution]).unique(subset=["MobileNumber", "CampaignName"]).collect().count()


# Join the datasets using the required customer-level key.
email_soft_oct_attribution = email_oct_data.join(softproduct_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


# Join the datasets using the required customer-level key.
email_soft_nov_attribution = email_nov_data.join(softproduct_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


pl.concat([email_soft_oct_attribution, email_soft_nov_attribution]).unique(subset=["SubscriberKey", "JourneyName"]).collect().count()


# ##### ***MAGENTO ATTRIBUTION***


# Apply column transformations and standardize the required fields.
magento_data = magento_data.with_columns(
    (pl.col("Mobile_Number")
    .str.strip_chars("+")  # Remove + from start/end
    .str.replace("^91", "")  # Remove 91 from start
    .cast(pl.Int64, strict=False)
    .alias("Mobile_Number")),
    (pl.col("sale_date").str.strptime(pl.Date, format="%Y-%m-%d").alias("sale_date"))
)


whatsapp_data.join(magento_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("EventDateUTC") <= pl.col("sale_date")).unique(subset=["MobileNumber"]).collect().count()


# Join the datasets using the required customer-level key.
email_mag_oct_attribution = email_oct_data.join(magento_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


# Join the datasets using the required customer-level key.
email_mag_nov_attribution = email_nov_data.join(magento_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


pl.concat([email_mag_oct_attribution, email_mag_nov_attribution]).unique(subset=["SubscriberKey", "JourneyName"]).collect().count()


# Join the datasets using the required customer-level key.
sms_mag_oct_attribution = sms_oct_data.join(magento_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("CreatedAt") <= pl.col("sale_date")).unique(subset=["MobileNumber", "CampaignName"]).select(["MobileNumber", "CampaignName"])


# Join the datasets using the required customer-level key.
sms_mag_nov_attribution = sms_nov_data.join(magento_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(
    (pl.col("ActionDateTime") <= pl.col("sale_date")) &
    (pl.col("Delivered") == 1)
).unique(subset=["MobileNumber"]).select(["MobileNumber", "CampaignName"])


sms_mag_nov_attribution.collect().head(1)


pl.concat([sms_mag_oct_attribution, sms_mag_nov_attribution]).unique(subset=["MobileNumber", "CampaignName"]).collect().count()


# ##### ***CDP GEAR ATTRIBUTION***


cdpgear_data.collect().head(1)


# Apply column transformations and standardize the required fields.
cdpgear_data = cdpgear_data.with_columns(pl.col("sale_date").str.strptime(pl.Date, format="%Y-%m-%d").alias("sale_date"))


# Join the datasets using the required customer-level key.
email_cdp_oct_attribution = email_oct_data.join(cdpgear_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


# Join the datasets using the required customer-level key.
email_cdp_nov_attribution = email_nov_data.join(cdpgear_data, left_on="SubscriberKey",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("OpenEventDate") <= pl.col("sale_date")).unique(subset=["SubscriberKey"])


pl.concat([email_cdp_oct_attribution, email_cdp_nov_attribution]).unique(subset=["SubscriberKey", "JourneyName"]).collect().count()


# Join the datasets using the required customer-level key.
sms_cdp_oct_attribution = sms_oct_data.join(cdpgear_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("CreatedAt") <= pl.col("sale_date")).unique(subset=["MobileNumber", "CampaignName"]).select(["MobileNumber", "CampaignName"])


# Join the datasets using the required customer-level key.
sms_cdp_nov_attribution = sms_nov_data.join(cdpgear_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(
    (pl.col("ActionDateTime") <= pl.col("sale_date")) &
    (pl.col("Delivered") == 1)
).unique(subset=["MobileNumber"]).select(["MobileNumber", "CampaignName"])


pl.concat([sms_cdp_oct_attribution, sms_cdp_nov_attribution]).unique(subset=["MobileNumber", "CampaignName"]).collect().count()


whatsapp_data.join(cdpgear_data, left_on="MobileNumber",
right_on="Mobile_Number",
how="inner"
).filter(pl.col("EventDateUTC") <= pl.col("sale_date")).unique(subset=["MobileNumber"]).collect().count()
