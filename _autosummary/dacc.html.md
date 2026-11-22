# dacc

### Functions

| [`ascertain_list`](#dacc.ascertain_list)(x)                          | ascertain_list(x) blah blah returns [x] if x is not already a list, and x itself if it's already a list Use: This is useful when a function expects a list, but you want to also input a single element without putting this this element in a list   |
|---------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`get_subdict_and_remainder`](#dacc.get_subdict_and_remainder)(d, list_of_keys) |                                                                                                                                                                                                                                                       |
| `has_non_callable_attr`(obj, attr)                                                          |                                                                                                                                                                                                                                                       |

### Classes

| [`DataFlow`](#dacc.DataFlow)(\*\*kwargs)   | DataFlow is a framework to pipeline data processes.   |
|-------------------------------------------------------------------------|-------------------------------------------------------|

### *class* dacc.DataFlow(\*\*kwargs)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

DataFlow is a framework to pipeline data processes.

### dacc.ascertain_list(x)

ascertain_list(x) blah blah returns [x] if x is not already a list, and x itself if it’s already a list
Use: This is useful when a function expects a list, but you want to also input a single element without putting this
this element in a list

### dacc.get_subdict_and_remainder(d, list_of_keys)

* **Parameters:**
  * **d** – dict
  * **subset_of_keys** – list of keys
* **Returns:**
  the subset of key:value pairs of d where key is in list_of_keys
