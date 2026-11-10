"""
Module: ifc_extractor
Descrption: Module for extracting elements, spatial context,
            and quantities from IFC (Industrial Foundation Classes) files
            using IfcOpenShell. Designed for modular BIM/GIS ETL pipelines.
"""

import logging
from typing import Generator, List, Dict, Any, Optional

import ifcopenshell
import ifcopenshell.util.element


class IfcExtractor:
    """
    A extractor for parsing BIM data from IFC files using generators(yield) and per-entity error isolaton,
    upports lightweight spatial ingestions as well as optional quantity extraction.
    """
    def __init__(self, file_path: str, logger: Optional[logging.Logger] = None)-> None:
        """Initializes the IFCExtractor with a target IFC file and an optional logger.

        Args:
            file_path (str): Path to the IFC file(.ifc).
            logger (Optional[logging.Logger]): Logger instance for tracking operations.
        """
        self.file_path = file_path
        self.logger = logger or logging.getLogger(__name__)
        self.ifc_file = self._load_file()

    def _load_file(self) -> ifcopenshell.file:
        """
        Safety loads the IFC file into memory.

        Returns:
            ifcopenshell.file: The loaded IFC file object.

        Raises:
            Exception: If the file cannot be opened or parsed.
        """
        self.logger.info("Loading IFC file: %s", self.file_path)
        try:
            ifc_model = ifcopenshell.open(self.file_path)
            self.logger.info("IFC file successfully loaded.")
            return ifc_model
        except Exception as e:
            self.logger.error("Failed to load IFC file '%s':%s", self.file_path, e)
            raise


    def extract_elements(
            self,
              entity_type: str = "IfcProduct",
              include_quantities: bool = False
              ) -> Generator[Dict[str, Any], None, None]:
        """
        Generator based extraction for basic attributes and spatial context for elements of a specific type.

        Args:
            entity_type (str): The IFC entity type (e.g., 'IfcWall', 'IfcSpace', 'IfcDoor').
            include_quantties (bool) : If True, parse heavy Propertyand Quantity sets
                                       in the same single pass.

        Yields:
            Dict[str, Any]]: Extraced raw metadata of a single element
        """
        elements = self.ifc_file.by_type(entity_type)
        total_elements = len(elements)
        self.logger.info(
            "Streaming %d elements of type %s (include_quantities=%s)",
            total_elements, 
            entity_type,
            include_quantities
            )

        success_count = 0
        error_count = 0

        for el in elements:
            try:
                #1. Spatial Decomposition (Safe Storey Lookup - 0(1) Pointer)
                storey_name = "Unknown Storey"
                try:
                    container = ifcopenshell.util.element.get_container(el)
                    if container and container.is_a("IfcBuildingStorey"):
                        storey_name = getattr(container, "Name", "Unnamed") or "Unnamed"
                except Exception:
                    pass 

                #2. Base Payload Assembly
                element_data:Dict[str, Any] = {
                "guid": getattr(el, "GlobalId", None),
                "type": el.is_a(),
                "name": getattr(el, "Name", "Unknown"),
                "storey": storey_name,
                "raw_attributes": el.get_info(),
                    }

                #3. Optional Single-Pass Quantity/Property Extraction 
                if include_quantities:
                    try:
                        # Extract property sets & quantity sets using standard utility
                        element_data["quantities"] = ifcopenshell.util.element.get_psets(
                            el, qtos_only = True
                        )
                        element_data["psets"] = ifcopenshell.util.element.get_psets(
                            el, psets_only = True
                        )
                    except Exception as q_err:
                        self.logger.debug(
                            "Could not parse quantities for entity %s: %s",
                            getattr(el, "GlobalId","Unknown"),
                            q_err
                        )
                        element_data["quantities"] = {}
                        element_data["psets"] = {}
 
                success_count += 1
                yield element_data

            except Exception as e:
                error_count += 1 
                self.logger.error(
                    "Error parsing entity ID %s: %s. Skipping element.",
                    el.id(),
                    e
                )

        self.logger.info(
            "Extraction complete. Successfully streamed: %s, Skipped (errors): %s",
            success_count,
            error_count
        )


