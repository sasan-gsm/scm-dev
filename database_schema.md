# SCM Database Schema

This document provides a comprehensive overview of the database schema for the Supply Chain Management (SCM) system, showing all tables and their relationships.

## Core Models

### TimeStampedModel (Abstract Base Class)
- **created_at**: DateTimeField
- **updated_at**: DateTimeField

## Accounts Module

### User
- **id**: PK
- **username**: CharField
- **email**: EmailField (unique)
- **phone_number**: CharField (unique, optional)
- **department_id**: FK → Department (optional)
- **position**: CharField
- **is_manager**: BooleanField
- **custom_permissions**: M2M → Permission
- *Inherits from*: AbstractUser, TimeStampedModel

### Department
- **id**: PK
- **name**: CharField
- **code**: CharField (unique)
- **manager_id**: FK → User (optional)
- **parent_id**: FK → Department (self-reference, optional)
- *Inherits from*: TimeStampedModel

### Permission
- **id**: PK
- **name**: CharField
- **codename**: CharField (unique)
- **description**: TextField
- **is_basic**: BooleanField
- *Inherits from*: TimeStampedModel

## Projects Module

### Project
- **id**: PK
- **name**: CharField
- **number**: CharField (unique)
- **start_date**: DateField
- **end_date**: DateField (optional)
- **weight_factor**: DecimalField
- **status**: CharField (choices)
- **manager_id**: FK → User
- **description**: TextField
- *Inherits from*: TimeStampedModel

## Materials Module

### MaterialCategory
- **id**: PK
- **name**: CharField
- **parent_id**: FK → MaterialCategory (self-reference, optional)
- *Inherits from*: TimeStampedModel

### Material
- **id**: PK
- **code**: CharField (unique)
- **name**: CharField
- **description**: TextField
- **category_id**: FK → MaterialCategory
- **unit_of_measure**: CharField
- **technical_specs**: JSONField
- **is_active**: BooleanField
- **created_by_id**: FK → User
- *Inherits from*: TimeStampedModel

### MaterialPriceHistory
- **id**: PK
- **material_id**: FK → Material
- **price**: DecimalField
- **effective_date**: DateField
- **recorded_by_id**: FK → User
- **notes**: TextField
- *Inherits from*: TimeStampedModel

## Request Module

### Request
- **id**: PK
- **number**: CharField (unique)
- **requester_id**: FK → User
- **project_id**: FK → Project
- **request_date**: DateField
- **required_date**: DateField
- **status**: CharField (choices)
- **priority**: CharField (choices)
- **notes**: TextField
- **fulfillment_date**: DateField (optional)
- *Inherits from*: TimeStampedModel

### RequestItem
- **id**: PK
- **request_id**: FK → Request
- **material_id**: FK → Material
- **quantity**: DecimalField
- **quantity_fulfilled**: DecimalField
- **is_fulfilled**: BooleanField
- **fulfillment_date**: DateField (optional)
- **status**: CharField (choices)
- **notes**: TextField
- *Inherits from*: TimeStampedModel

## Procurement Module

### Supplier
- **id**: PK
- **name**: CharField
- **code**: CharField (unique)
- **contact_person**: CharField
- **email**: EmailField
- **phone**: CharField
- **address**: TextField
- **is_active**: BooleanField
- *Inherits from*: TimeStampedModel

### SupplierContact
- **id**: PK
- **supplier_id**: FK → Supplier
- **name**: CharField
- **position**: CharField
- **email**: EmailField
- **phone**: CharField
- **is_primary**: BooleanField
- **notes**: TextField
- *Inherits from*: TimeStampedModel

### PurchaseOrder
- **id**: PK
- **supplier_id**: FK → Supplier
- **order_number**: CharField (unique)
- **order_date**: DateField
- **expected_delivery**: DateField (optional)
- **status**: CharField (choices)
- **created_by_id**: FK → User
- **notes**: TextField
- *Inherits from*: TimeStampedModel

### PurchaseOrderItem
- **id**: PK
- **purchase_order_id**: FK → PurchaseOrder
- **request_item_id**: FK → RequestItem (optional)
- **material_id**: FK → Material
- **quantity**: DecimalField
- **received_quantity**: DecimalField
- *Inherits from*: TimeStampedModel

## Inventory Module

### Warehouse
- **id**: PK
- **name**: CharField
- **code**: CharField (unique)
- **location**: CharField
- **is_active**: BooleanField
- *Inherits from*: TimeStampedModel

### InventoryLocation
- **id**: PK
- **warehouse_id**: FK → Warehouse
- **name**: CharField
- **code**: CharField
- *Inherits from*: TimeStampedModel
- *Unique together*: (warehouse, code)

### InventoryItem
- **id**: PK
- **material_id**: FK → Material
- **warehouse_id**: FK → Warehouse
- **location_id**: FK → InventoryLocation (optional)
- **quantity**: DecimalField
- **min_quantity**: DecimalField
- **monitor_stock_level**: BooleanField
- *Inherits from*: TimeStampedModel
- *Unique together*: (material, warehouse, location)

### InventoryTransaction
- **id**: PK
- **material_id**: FK → Material
- **transaction_type**: CharField (choices)
- **quantity**: DecimalField
- **from_warehouse_id**: FK → Warehouse (optional)
- **to_warehouse_id**: FK → Warehouse (optional)
- **project_id**: FK → Project (optional)
- **purchase_order_item_id**: FK → PurchaseOrderItem (optional)
- **performed_by_id**: FK → User
- **is_general_use**: BooleanField
- **notes**: TextField
- *Inherits from*: TimeStampedModel

## Quality Module

### QualityStandard
- **id**: PK
- **name**: CharField
- **code**: CharField (unique)
- **description**: TextField
- **criteria**: TextField
- **is_active**: BooleanField
- *Inherits from*: TimeStampedModel

### QualityCheck
- **id**: PK
- **check_number**: CharField (unique)
- **project_id**: FK → Project
- **material_id**: FK → Material
- **inventory_transaction_id**: FK → InventoryTransaction (optional)
- **check_date**: DateTimeField
- **inspector_id**: FK → User
- **location**: CharField
- **batch_number**: CharField
- **status**: CharField (choices)
- **notes**: TextField
- *Inherits from*: TimeStampedModel

### QualityCheckItem
- **id**: PK
- **quality_check_id**: FK → QualityCheck
- **standard_id**: FK → QualityStandard
- **result**: CharField
- **notes**: TextField
- **is_passed**: BooleanField
- *Inherits from*: TimeStampedModel

## Accounting Module

### AccountingEntry
- **id**: PK
- **inventory_transaction_id**: FK → InventoryTransaction (optional)
- **unit_price**: DecimalField
- **total_price**: DecimalField
- **currency**: CharField
- **set_by_id**: FK → User
- **set_date**: DateTimeField
- **approved_by_id**: FK → User (optional)
- **approved_date**: DateTimeField (optional)
- **status**: CharField (choices)
- **notes**: TextField
- *Inherits from*: TimeStampedModel

### GeneralExpense
- **id**: PK
- **description**: CharField
- **amount**: DecimalField
- **expense_date**: DateField
- **allocation_type**: CharField (choices)
- **project_id**: FK → Project (optional)
- **created_by_id**: FK → User
- **approved_by_id**: FK → User (optional)
- *Inherits from*: TimeStampedModel

### ExpenseCategory
- **id**: PK
- **name**: CharField (unique)
- **description**: TextField
- **is_active**: BooleanField
- **parent_id**: FK → ExpenseCategory (self-reference, optional)
- *Inherits from*: TimeStampedModel

### ProjectIncome
- **id**: PK
- **project_id**: FK → Project
- **description**: CharField
- **amount**: DecimalField
- **income_date**: DateField
- **created_by_id**: FK → User
- **approved_by_id**: FK → User (optional)
- *Inherits from*: TimeStampedModel

### Budget
- **id**: PK
- **budget_number**: CharField (unique)
- **name**: CharField
- **description**: TextField
- **project_id**: FK → Project (optional)
- **status**: CharField (choices)
- *Inherits from*: TimeStampedModel

### BudgetItem
- **id**: PK
- **budget_id**: FK → Budget
- **description**: CharField
- **amount**: DecimalField
- **category_id**: FK → ExpenseCategory (optional)
- **notes**: TextField
- *Inherits from*: TimeStampedModel

### Invoice
- **id**: PK
- **invoice_number**: CharField (unique)
- **supplier_id**: FK → Supplier (optional)
- **project_id**: FK → Project (optional)
- **amount**: DecimalField
- **issue_date**: DateField
- **due_date**: DateField
- **status**: CharField (choices)
- **notes**: TextField
- *Inherits from*: TimeStampedModel

### Payment
- **id**: PK
- **payment_number**: CharField (unique)
- **invoice_id**: FK → Invoice (optional)
- **amount**: DecimalField
- **payment_date**: DateField
- **payment_method**: CharField (choices)
- **reference_number**: CharField
- **notes**: TextField
- *Inherits from*: TimeStampedModel

## Notifications Module

### AlertRule
- **id**: PK
- **name**: CharField
- **alert_type**: CharField (choices)
- **created_by_id**: FK → User
- **is_active**: BooleanField
- **send_email**: BooleanField
- **send_in_app**: BooleanField
- **material_id**: FK → Material (optional)
- **content_type_id**: FK → ContentType (optional)
- **object_id**: PositiveIntegerField (optional)
- **content_object**: GenericForeignKey
- *Inherits from*: TimeStampedModel

### Notification
- **id**: PK
- **user_id**: FK → User
- **title**: CharField
- **message**: TextField
- **is_read**: BooleanField
- **alert_rule_id**: FK → AlertRule (optional)
- **notification_type**: CharField (optional)
- **read_at**: DateTimeField (optional)
- **content_type_id**: FK → ContentType (optional)
- **object_id**: PositiveIntegerField (optional)
- **content_object**: GenericForeignKey
- *Inherits from*: TimeStampedModel

### NotificationSetting
- **id**: PK
- **user_id**: FK → User
- **notification_type**: CharField (choices)
- **email_enabled**: BooleanField
- **push_enabled**: BooleanField
- **in_app_enabled**: BooleanField
- *Inherits from*: TimeStampedModel
- *Unique together*: (user, notification_type)

### NotificationTemplate
- **id**: PK
- **code**: CharField (unique)
- **notification_type**: CharField
- **subject**: CharField
- **body**: TextField
- **is_active**: BooleanField
- *Inherits from*: TimeStampedModel

## Attachments Module

### Attachment
- **id**: PK
- **file**: FileField
- **name**: CharField
- **description**: TextField
- **content_type_id**: FK → ContentType
- **object_id**: PositiveIntegerField
- **content_object**: GenericForeignKey
- **uploaded_by_id**: FK → User
- **file_type**: CharField
- **file_size**: PositiveIntegerField
- *Inherits from*: TimeStampedModel

## Relationship Diagram

```
+----------------+       +----------------+       +----------------+
|     User       |       |   Department   |       |   Permission   |
+----------------+       +----------------+       +----------------+
| id             |<----->| id             |       | id             |
| username       |       | name           |       | name           |
| email          |       | code           |       | codename       |
| phone_number   |       | manager_id     |------>| description    |
| department_id  |------>| parent_id      |       | is_basic       |
| position       |       +----------------+       +----------------+
| is_manager     |                                       ^
| custom_perms   |---------------------------------------+
+----------------+
        ^                                    +----------------+
        |                                    |    Project     |
        |                                    +----------------+
        |                                    | id             |
        |                                    | name           |
        +-----------------------------------<| number         |
                                             | start_date     |
                                             | end_date       |
                                             | weight_factor  |
                                             | status         |
                                             | manager_id     |
                                             | description    |
                                             +----------------+
                                                     ^
                                                     |
+----------------+       +----------------+          |
| MaterialCategory|       |    Material    |          |
+----------------+       +----------------+          |
| id             |       | id             |          |
| name           |       | code           |          |
| parent_id      |<------| name           |          |
+----------------+       | description    |          |
                         | category_id    |          |
                         | unit_of_measure|          |
                         | technical_specs|          |
                         | is_active      |          |
                         | created_by_id  |          |
                         +----------------+          |
                                 ^                   |
                                 |                   |
+----------------+       +----------------+          |
|MaterialPriceHist|       |    Request     |          |
+----------------+       +----------------+          |
| id             |       | id             |          |
| material_id    |<------| number         |          |
| price          |       | requester_id   |          |
| effective_date |       | project_id     |----------+
| recorded_by_id |       | request_date   |
| notes          |       | required_date  |
+----------------+       | status         |
                         | priority       |
                         | notes          |
                         | fulfillment_date|
                         +----------------+
                                 ^
                                 |
+----------------+       +----------------+       +----------------+
|   RequestItem  |       |    Supplier    |       |SupplierContact |
+----------------+       +----------------+       +----------------+
| id             |       | id             |       | id             |
| request_id     |       | name           |       | supplier_id    |
| material_id    |       | code           |       | name           |
| quantity       |       | contact_person |       | position       |
| quantity_fulfil|       | email          |       | email          |
| is_fulfilled   |       | phone          |       | phone          |
| fulfillment_date|      | address        |       | is_primary     |
| status         |       | is_active      |       | notes          |
| notes          |       +----------------+       +----------------+
+----------------+              ^
        ^                        |
        |                        |
        |                        |
        |                        |
+----------------+       +----------------+
| PurchaseOrder  |       |PurchaseOrderItem|
+----------------+       +----------------+
| id             |       | id             |
| supplier_id    |------>| purchase_order_id|
| order_number   |       | request_item_id|----+
| order_date     |       | material_id    |    |
| expected_deliv |       | quantity       |    |
| status         |       | received_quant |    |
| created_by_id  |       +----------------+    |
| notes          |              ^              |
+----------------+              |              |
                                |              |
                                |              |
+----------------+       +----------------+    |
|   Warehouse    |       | InventoryItem  |    |
+----------------+       +----------------+    |
| id             |       | id             |    |
| name           |       | material_id    |    |
| code           |       | warehouse_id   |    |
| location       |       | location_id    |    |
| is_active      |       | quantity       |    |
+----------------+       | min_quantity   |    |
        ^                | monitor_stock  |    |
        |                +----------------+    |
        |                                      |
        |                                      |
+----------------+       +----------------+    |
|InventoryLocation|      |InventoryTransact|    |
+----------------+       +----------------+    |
| id             |       | id             |    |
| warehouse_id   |------>| material_id    |    |
| name           |       | transaction_type|    |
| code           |       | quantity       |    |
+----------------+       | from_warehouse |    |
                         | to_warehouse   |    |
                         | project_id     |    |
                         | purchase_order_|----+
                         | performed_by_id|    
                         | is_general_use |    
                         | notes          |    
                         +----------------+    
```

## Key Relationships

1. **User** belongs to a **Department** and can manage multiple **Departments**
2. **Department** has a hierarchical structure with parent-child relationships
3. **User** can have multiple **Permissions**
4. **Project** is managed by a **User**
5. **Material** belongs to a **MaterialCategory** and has price history tracked in **MaterialPriceHistory**
6. **Request** is created by a **User** for a specific **Project**
7. **RequestItem** belongs to a **Request** and references a specific **Material**
8. **Supplier** has multiple **SupplierContacts**
9. **PurchaseOrder** is created for a **Supplier** and contains multiple **PurchaseOrderItems**
10. **PurchaseOrderItem** can be linked to a **RequestItem** and a specific **Material**
11. **Warehouse** contains multiple **InventoryLocations**
12. **InventoryItem** tracks quantity of a **Material** in a specific **Warehouse** and **InventoryLocation**
13. **InventoryTransaction** records movement of **Material** between **Warehouses** or for a **Project**
14. **QualityCheck** is performed on a **Material** for a **Project** and can be linked to an **InventoryTransaction**
15. **QualityCheckItem** belongs to a **QualityCheck** and references a **QualityStandard**
16. **AccountingEntry** can be linked to an **InventoryTransaction**
17. **Budget** can be associated with a **Project** and contains multiple **BudgetItems**
18. **Invoice** can be linked to a **Supplier** and/or a **Project**
19. **Payment** can be linked to an **Invoice**
20. **AlertRule** can reference a **Material** or any other object through **GenericForeignKey**
21. **Notification** is sent to a **User** and can be linked to an **AlertRule**
22. **Attachment** can be linked to any object through **GenericForeignKey**

This schema represents a comprehensive Supply Chain Management system with modules for managing users, projects, materials, procurement, inventory, quality control, accounting, and notifications.